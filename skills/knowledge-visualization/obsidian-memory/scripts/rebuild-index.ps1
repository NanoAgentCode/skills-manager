[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$VaultPath
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $VaultPath -PathType Container)) { throw "找不到 Obsidian Vault：$VaultPath" }

$vault = (Resolve-Path -LiteralPath $VaultPath).Path.TrimEnd("\")
$systemDirectory = Join-Path $vault "90-System"
$indexPath = Join-Path $systemDirectory "Codex-Memory-Index.md"
if (-not (Test-Path -LiteralPath $systemDirectory)) { New-Item -ItemType Directory -Path $systemDirectory | Out-Null }

$categories = [ordered]@{
    "项目记忆" = "10-Projects"
    "稳定知识" = "20-Knowledge"
    "历史决策" = "30-Decisions"
    "用户偏好" = "40-Preferences"
}

$lines = [System.Collections.Generic.List[string]]::new()
@("---", "type: memory-index", "status: active", "updated: $(Get-Date -Format 'yyyy-MM-dd')", "tags:", "  - codex-memory", "  - index", "---", "", "# Codex 记忆索引", "", '> 本页由 rebuild-index.ps1 生成，只收录正式记忆目录，不收录候选记忆。', "", "- [[首页|返回记忆库首页]]", "- [[90-System/Memory-Rules|记忆管理规则]]") | ForEach-Object { $lines.Add($_) }

foreach ($entry in $categories.GetEnumerator()) {
    $lines.Add(""); $lines.Add("## $($entry.Key)"); $lines.Add("")
    $directory = Join-Path $vault $entry.Value
    $files = if (Test-Path -LiteralPath $directory) { @(Get-ChildItem -LiteralPath $directory -Recurse -File -Filter "*.md" | Where-Object { $_.Name -ne "_说明.md" } | Sort-Object FullName) } else { @() }
    if (-not $files) { $lines.Add("- 暂无正式记忆"); continue }

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Encoding UTF8
        $heading = $content | Where-Object { $_ -match '^#\s+(.+)$' } | Select-Object -First 1
        $title = if ($heading) { $heading -replace '^#\s+', '' } else { $file.BaseName }
        $statusLine = $content | Where-Object { $_ -match '^status:\s*(.+)$' } | Select-Object -First 1
        $status = if ($statusLine) { ($statusLine -replace '^status:\s*', '').Trim() } else { "未标记" }
        $relative = $file.FullName.Substring($vault.Length).TrimStart("\")
        $linkPath = $relative.Substring(0, $relative.Length - $file.Extension.Length).Replace("\", "/")
        $lines.Add("- [[$linkPath|$title]]（状态：$status）")
    }
}

$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($indexPath, $lines, $utf8WithoutBom)
Write-Output "已重建记忆索引：$indexPath"
