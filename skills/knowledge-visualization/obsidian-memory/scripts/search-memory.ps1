[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [string]$VaultPath = "D:\WorkSpace\AgentVault",
    [ValidateSet("", "00-Inbox", "10-Projects", "20-Knowledge", "30-Decisions", "40-Preferences", "90-System")]
    [string]$Scope = "",
    [ValidateSet("All", "Any")]
    [string]$MatchMode = "All",
    [ValidateRange(1, 200)]
    [int]$Limit = 20
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $VaultPath -PathType Container)) { throw "找不到 Obsidian Vault：$VaultPath" }

function Get-SearchTerms {
    param([string]$Text)

    $seen = @{}
    $terms = foreach ($match in [regex]::Matches($Text, '"([^"]+)"|[^\s,，;；]+')) {
        $value = if ($match.Groups[1].Success) { $match.Groups[1].Value } else { $match.Value }
        $value = $value.Trim()
        if (-not $value) { continue }
        $key = $value.ToLowerInvariant()
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            $value
        }
    }
    return @($terms)
}

function Test-ContainsLiteral {
    param([string]$Text, [string]$Term)
    return $Text.IndexOf($Term, [StringComparison]::OrdinalIgnoreCase) -ge 0
}

function Get-LiteralCount {
    param([string]$Text, [string]$Term)
    return [regex]::Matches(
        $Text,
        [regex]::Escape($Term),
        [Text.RegularExpressions.RegexOptions]::IgnoreCase
    ).Count
}

$terms = @(Get-SearchTerms $Query)
if (-not $terms) { throw "查询至少包含一个有效关键词。" }

$vault = (Resolve-Path -LiteralPath $VaultPath).Path.TrimEnd("\")
$defaultScopes = @("00-Inbox", "10-Projects", "20-Knowledge", "30-Decisions", "40-Preferences", "90-System")
$scopeNames = if ([string]::IsNullOrWhiteSpace($Scope)) { $defaultScopes } else { @($Scope) }
$searchRoots = foreach ($scopeName in $scopeNames) {
    $candidate = Join-Path $vault $scopeName
    if (Test-Path -LiteralPath $candidate -PathType Container) { $candidate }
}

if (-not $searchRoots) { Write-Output "没有可搜索的记忆目录。"; return }
$files = @($searchRoots | ForEach-Object { Get-ChildItem -LiteralPath $_ -Recurse -File -Filter "*.md" })
if (-not $files) { Write-Output "记忆库中还没有 Markdown 文件。"; return }

$results = foreach ($file in $files) {
    $content = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)
    $lines = @($content -split "\r?\n")
    $titleLine = @($lines | Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
    $title = if ($titleLine) { $titleLine[0] } else { "" }
    $tagMatch = [regex]::Match($content, '(?ms)^tags:[ \t]*\r?\n((?:[ \t]+-[^\r\n]*(?:\r?\n|$))*)')
    $tags = if ($tagMatch.Success) { $tagMatch.Groups[1].Value } else { "" }

    $matchedTerms = @()
    $score = 0
    foreach ($term in $terms) {
        $inContent = Test-ContainsLiteral $content $term
        $inName = Test-ContainsLiteral $file.BaseName $term
        if (-not $inContent -and -not $inName) { continue }

        $matchedTerms += $term
        if ($inName) { $score += 30 }
        if (Test-ContainsLiteral $title $term) { $score += 20 }
        if (Test-ContainsLiteral $tags $term) { $score += 10 }
        if ($inContent) { $score += [Math]::Min((Get-LiteralCount $content $term), 20) }
    }

    $isMatch = if ($MatchMode -eq "All") {
        $matchedTerms.Count -eq $terms.Count
    } else {
        $matchedTerms.Count -gt 0
    }
    if (-not $isMatch) { continue }

    $bestLineNumber = 1
    $bestLine = if ($title) { $title } else { $lines[0] }
    $bestLineScore = -1
    for ($index = 0; $index -lt $lines.Count; $index++) {
        $line = $lines[$index]
        if (-not $line.Trim()) { continue }
        $lineTermCount = @($matchedTerms | Where-Object { Test-ContainsLiteral $line $_ }).Count
        if ($lineTermCount -eq 0) { continue }
        $lineScore = $lineTermCount * 10
        if ($line -match '^#\s+') { $lineScore += 5 }
        if ($line -match '^\s+-\s+') { $lineScore += 1 }
        if ($lineScore -gt $bestLineScore) {
            $bestLineScore = $lineScore
            $bestLineNumber = $index + 1
            $bestLine = $line.Trim()
        }
    }
    if ($bestLine.Length -gt 200) { $bestLine = $bestLine.Substring(0, 197) + "..." }

    [pscustomobject]@{
        RelativePath = $file.FullName.Substring($vault.Length).TrimStart("\")
        LineNumber = $bestLineNumber
        Line = $bestLine
        Score = $score
        MatchedTerms = $matchedTerms
    }
}

if (-not $results) {
    Write-Output ("未找到匹配 [{0}] 的记忆（模式：{1}）。" -f ($terms -join " "), $MatchMode)
    return
}

$sortedResults = @($results | Sort-Object `
    @{ Expression = { $_.Score }; Descending = $true }, `
    @{ Expression = { $_.RelativePath }; Descending = $false } | Select-Object -First $Limit)

foreach ($result in $sortedResults) {
    $keywords = $result.MatchedTerms -join ","
    Write-Output ("{0}:{1}: [score={2}; keywords={3}] {4}" -f `
        $result.RelativePath, $result.LineNumber, $result.Score, $keywords, $result.Line)
}
