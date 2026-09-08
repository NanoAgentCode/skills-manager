$ErrorActionPreference = 'Stop'

$skillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$auditScript = Join-Path $skillRoot 'scripts\audit-memory-vault.ps1'
$temporaryVault = Join-Path ([IO.Path]::GetTempPath()) ("obsidian-memory-cleanup-test-" + [guid]::NewGuid().ToString('N'))

function Write-Utf8File {
    param([string]$Path, [string]$Content)

    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    [IO.File]::WriteAllText($Path, $Content, (New-Object Text.UTF8Encoding($false)))
}

function Invoke-Audit {
    param([string]$TestVaultPath)

    $shell = (Get-Process -Id $PID).Path
    $output = & $shell -NoProfile -ExecutionPolicy Bypass -File $auditScript -VaultPath $TestVaultPath -Json 2>&1
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Output = ($output -join "`n")
    }
}

try {
    foreach ($directory in @('10-Projects', '20-Knowledge', '30-Decisions', '40-Preferences', '90-System')) {
        New-Item -ItemType Directory -Path (Join-Path $temporaryVault $directory) -Force | Out-Null
    }

    $validNote = @'
---
type: memory
scope: demo
status: active
source: project-file
created: 2026-09-08
updated: 2026-09-08
tags:
  - codex-memory
related: []
superseded_by:
---

# 示例项目背景

## 记忆摘要

这是用于验证审计脚本的完整正式记忆，包含足够长且不重复的正文内容。
'@
    Write-Utf8File (Join-Path $temporaryVault '10-Projects\demo.md') $validNote
    Write-Utf8File (Join-Path $temporaryVault '90-System\Codex-Memory-Index.md') "# Index`n"

    $validResult = Invoke-Audit $temporaryVault
    if ($validResult.ExitCode -ne 0) {
        throw "有效 Vault 审计失败：$($validResult.Output)"
    }

    $brokenNote = $validNote -replace 'related: \[\]', "related:`n  - `"[[missing-note]]`""
    Write-Utf8File (Join-Path $temporaryVault '20-Knowledge\broken.md') $brokenNote
    $brokenResult = Invoke-Audit $temporaryVault
    if ($brokenResult.ExitCode -eq 0 -or $brokenResult.Output -notmatch 'broken-wikilink') {
        throw "断链没有被识别：$($brokenResult.Output)"
    }

    $candidateNote = $validNote -replace 'status: active', 'status: candidate'
    Write-Utf8File (Join-Path $temporaryVault '20-Knowledge\candidate.md') $candidateNote
    $candidateResult = Invoke-Audit $temporaryVault
    if ($candidateResult.ExitCode -eq 0 -or $candidateResult.Output -notmatch 'candidate-in-formal-directory') {
        throw "正式目录候选记忆没有被识别：$($candidateResult.Output)"
    }

    Write-Output 'PASS: audit-memory-vault.ps1'
} finally {
    if (Test-Path -LiteralPath $temporaryVault) {
        Remove-Item -LiteralPath $temporaryVault -Recurse -Force
    }
}

exit 0
