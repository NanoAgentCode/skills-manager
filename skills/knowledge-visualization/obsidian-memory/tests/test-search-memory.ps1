$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "..\scripts\search-memory.ps1"
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("obsidian-memory-search-test-" + [guid]::NewGuid().ToString("N"))

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "断言失败：$Message" }
}

function Write-Fixture {
    param([string]$RelativePath, [string]$Content)
    $path = Join-Path $tempRoot $RelativePath
    $directory = Split-Path $path -Parent
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    [IO.File]::WriteAllText($path, $Content, [Text.UTF8Encoding]::new($false))
}

try {
    Write-Fixture "20-Knowledge\rag-vector.md" @"
---
tags:
  - RAG
  - 向量检索
---
# RAG 与向量检索链路

文档分块后写入向量数据库，并按相关度召回。
"@
    Write-Fixture "20-Knowledge\rag-only.md" @"
# RAG 基础

这里只介绍文档增强生成。
"@
    Write-Fixture "20-Knowledge\agent-title.md" @"
---
tags:
  - Agent
  - 审批
---
# Agent 工具审批链路

工具调用通过后端门禁。
"@
    Write-Fixture "20-Knowledge\agent-body.md" @"
# 运行说明

Agent 在执行工具前等待审批。
"@
    Write-Fixture "40-Preferences\writing.md" @"
# 中文写作偏好

技术文章保持术语准确。
"@

    $allResult = @(& $scriptPath -Query "RAG 向量检索" -MatchMode All -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($allResult.Count -eq 1) "All 模式应只返回同时包含全部关键词的文件"
    Assert-True ($allResult[0] -match 'rag-vector\.md') "All 模式应命中 RAG 向量检索文件"
    Assert-True ($allResult[0] -match 'keywords=RAG,向量检索') "输出应解释命中的关键词"

    $phraseResult = @(& $scriptPath -Query '"向量检索" RAG' -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($phraseResult.Count -eq 1 -and $phraseResult[0] -match 'rag-vector\.md') "双引号短语应作为一个检索词"

    $punctuationResult = @(& $scriptPath -Query "rag，向量检索" -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($punctuationResult.Count -eq 1 -and $punctuationResult[0] -match 'rag-vector\.md') "中文标点应分隔关键词且英文匹配不区分大小写"

    $anyResult = @(& $scriptPath -Query "RAG 向量检索" -MatchMode Any -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($anyResult.Count -eq 2) "Any 模式应返回命中任一关键词的文件"

    $singleResult = @(& $scriptPath -Query "向量检索" -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($singleResult.Count -eq 1 -and $singleResult[0] -match 'rag-vector\.md') "单关键词行为应保持可用"

    $rankedResult = @(& $scriptPath -Query "Agent 审批" -Scope "20-Knowledge" -VaultPath $tempRoot)
    Assert-True ($rankedResult.Count -eq 2) "两个同时命中关键词的文件都应返回"
    Assert-True ($rankedResult[0] -match 'agent-title\.md') "标题和标签命中应排在仅正文命中之前"

    $limitedResult = @(& $scriptPath -Query "Agent 审批" -Scope "20-Knowledge" -Limit 1 -VaultPath $tempRoot)
    Assert-True ($limitedResult.Count -eq 1) "Limit 应限制返回文件数量"

    $scopeResult = @(& $scriptPath -Query "术语" -Scope "40-Preferences" -VaultPath $tempRoot)
    Assert-True ($scopeResult.Count -eq 1 -and $scopeResult[0] -match 'writing\.md') "Scope 应限制检索目录"

    $noMatch = @(& $scriptPath -Query "不存在的关键词" -VaultPath $tempRoot)
    Assert-True ($noMatch.Count -eq 1 -and $noMatch[0] -match '未找到匹配') "无结果时应返回明确提示"

    $emptyFailed = $false
    try { & $scriptPath -Query "   " -VaultPath $tempRoot | Out-Null } catch { $emptyFailed = $true }
    Assert-True $emptyFailed "空查询应被拒绝"

    Write-Output "PASS: search-memory 多关键词检索测试全部通过"
}
finally {
    $resolvedTemp = [IO.Path]::GetFullPath($tempRoot)
    $systemTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($systemTemp, [StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath $resolvedTemp)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
