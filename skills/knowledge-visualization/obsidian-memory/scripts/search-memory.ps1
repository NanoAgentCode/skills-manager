[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [string]$VaultPath = "D:\WorkSpace\AgentVault",
    [ValidateSet("", "00-Inbox", "10-Projects", "20-Knowledge", "30-Decisions", "40-Preferences", "90-System")]
    [string]$Scope = "",
    [ValidateRange(1, 200)]
    [int]$Limit = 20
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $VaultPath -PathType Container)) { throw "找不到 Obsidian Vault：$VaultPath" }

$vault = (Resolve-Path -LiteralPath $VaultPath).Path.TrimEnd("\")
$defaultScopes = @("00-Inbox", "10-Projects", "20-Knowledge", "30-Decisions", "40-Preferences", "90-System")
$scopeNames = if ([string]::IsNullOrWhiteSpace($Scope)) { $defaultScopes } else { @($Scope) }
$searchRoots = foreach ($scopeName in $scopeNames) {
    $candidate = Join-Path $vault $scopeName
    if (Test-Path -LiteralPath $candidate -PathType Container) { $candidate }
}

if (-not $searchRoots) { Write-Output "没有可搜索的记忆目录。"; exit 0 }
$files = @($searchRoots | ForEach-Object { Get-ChildItem -LiteralPath $_ -Recurse -File -Filter "*.md" })
if (-not $files) { Write-Output "记忆库中还没有 Markdown 文件。"; exit 0 }

$matches = @(Select-String -Path $files.FullName -Pattern $Query -SimpleMatch -Encoding UTF8 | Select-Object -First $Limit)
if (-not $matches) { Write-Output "未找到包含“$Query”的记忆。"; exit 0 }

foreach ($match in $matches) {
    $relativePath = $match.Path.Substring($vault.Length).TrimStart("\")
    Write-Output ("{0}:{1}: {2}" -f $relativePath, $match.LineNumber, $match.Line.Trim())
}
