[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$VaultPath,

    [ValidateRange(0.1, 1.0)]
    [double]$SimilarityThreshold = 0.45,

    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Add-Finding {
    param(
        [string]$Severity,
        [string]$Code,
        [string]$Path,
        [string]$Message
    )

    $script:Findings.Add([pscustomobject]@{
        severity = $Severity
        code = $Code
        path = $Path
        message = $Message
    }) | Out-Null
}

function Get-FrontmatterAndBody {
    param([string]$Content)

    if ($Content -notmatch '\A---\r?\n') {
        return $null
    }

    $parts = [regex]::Split($Content, '(?m)^---\s*$')
    if ($parts.Count -lt 3) {
        return $null
    }

    return [pscustomobject]@{
        Frontmatter = $parts[1]
        Body = (($parts | Select-Object -Skip 2) -join "`n")
    }
}

function Get-CoreLines {
    param([string]$Body)

    $result = New-Object 'System.Collections.Generic.HashSet[string]'
    $skipTail = $false
    foreach ($line in ($Body -split '\r?\n')) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^##\s+(变更记录|关联记忆)\s*$') {
            $skipTail = $true
            continue
        }
        if ($skipTail -or $trimmed -eq '' -or $trimmed -match '^#') {
            continue
        }

        $normalized = $trimmed `
            -replace '\[\[[^\]]+\]\]', '<link>' `
            -replace '`[^`]+`', '<code>' `
            -replace '\s+', ' '
        if ($normalized.Length -ge 18 -and $normalized -notmatch '^[-*]\s*<link>') {
            $result.Add($normalized) | Out-Null
        }
    }
    return $result
}

$resolvedVault = (Resolve-Path -LiteralPath $VaultPath).Path
$formalDirectories = @('10-Projects', '20-Knowledge', '30-Decisions', '40-Preferences')
$requiredFields = @('type', 'scope', 'status', 'source', 'created', 'updated', 'tags', 'related', 'superseded_by')
$allowedStatuses = @('active', 'uncertain', 'stale', 'superseded')
$allowedSources = @('user-confirmed', 'project-file', 'verified-result', 'inferred')
$Findings = New-Object 'System.Collections.Generic.List[object]'
$formalFiles = New-Object 'System.Collections.Generic.List[object]'

foreach ($directory in $formalDirectories) {
    $fullDirectory = Join-Path $resolvedVault $directory
    if (-not (Test-Path -LiteralPath $fullDirectory -PathType Container)) {
        Add-Finding 'error' 'missing-formal-directory' $directory '缺少正式记忆目录。'
        continue
    }

    Get-ChildItem -LiteralPath $fullDirectory -Recurse -File -Filter '*.md' |
        Where-Object { $_.Name -ne '_说明.md' } |
        ForEach-Object { $formalFiles.Add($_) | Out-Null }
}

$allMarkdown = Get-ChildItem -LiteralPath $resolvedVault -Recurse -File -Filter '*.md' |
    Where-Object { $_.FullName -notmatch '[\\/](\.obsidian|\.trash)[\\/]' }
$stemMap = @{}
foreach ($file in $allMarkdown) {
    if (-not $stemMap.ContainsKey($file.BaseName)) {
        $stemMap[$file.BaseName] = New-Object 'System.Collections.Generic.List[string]'
    }
    $stemMap[$file.BaseName].Add($file.FullName) | Out-Null
}

$noteRecords = New-Object 'System.Collections.Generic.List[object]'
foreach ($file in $formalFiles) {
    $relativePath = $file.FullName.Substring($resolvedVault.Length).TrimStart('\', '/')
    $content = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    $parsed = Get-FrontmatterAndBody $content
    if ($null -eq $parsed) {
        Add-Finding 'error' 'invalid-frontmatter' $relativePath 'Frontmatter 缺失或未闭合。'
        continue
    }

    foreach ($field in $requiredFields) {
        if ($parsed.Frontmatter -notmatch "(?m)^$([regex]::Escape($field)):") {
            Add-Finding 'error' 'missing-frontmatter-field' $relativePath "缺少字段：$field。"
        }
    }

    $status = ''
    if ($parsed.Frontmatter -match '(?m)^status:\s*([^\s#]+)') {
        $status = $Matches[1].Trim('"', "'")
        if ($status -eq 'candidate') {
            Add-Finding 'error' 'candidate-in-formal-directory' $relativePath '候选记忆不得位于正式目录。'
        } elseif ($status -notin $allowedStatuses) {
            Add-Finding 'error' 'invalid-status' $relativePath "正式记忆状态无效：$status。"
        }
    }

    if ($parsed.Frontmatter -match '(?m)^source:\s*([^\s#]+)') {
        $source = $Matches[1].Trim('"', "'")
        if ($source -notin $allowedSources) {
            Add-Finding 'warning' 'nonstandard-source' $relativePath "来源字段需要人工确认：$source。"
        }
    }

    foreach ($dateField in @('created', 'updated')) {
        if ($parsed.Frontmatter -notmatch "(?m)^${dateField}:\s*\d{4}-\d{2}-\d{2}\s*$") {
            Add-Finding 'error' 'invalid-date' $relativePath "$dateField 必须使用 YYYY-MM-DD。"
        }
    }

    if ($status -eq 'superseded' -and $parsed.Frontmatter -notmatch '(?m)^superseded_by:\s*\S+') {
        Add-Finding 'error' 'missing-superseded-target' $relativePath 'superseded 记忆必须填写 superseded_by。'
    }

    foreach ($match in [regex]::Matches($content, '\[\[([^\]|#]+)')) {
        $originalTarget = $match.Groups[1].Value.Trim()
        if ($originalTarget -eq '双向链接') {
            continue
        }
        $target = $originalTarget.Replace('/', [IO.Path]::DirectorySeparatorChar)

        if ($target.Contains([IO.Path]::DirectorySeparatorChar)) {
            if (-not $target.EndsWith('.md', [StringComparison]::OrdinalIgnoreCase)) {
                $target += '.md'
            }
            $candidate = Join-Path $resolvedVault $target
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
                Add-Finding 'error' 'broken-wikilink' $relativePath "链接目标不存在：$originalTarget。"
            }
        } else {
            $leaf = [IO.Path]::GetFileNameWithoutExtension($target)
            if (-not $stemMap.ContainsKey($leaf)) {
                Add-Finding 'error' 'broken-wikilink' $relativePath "链接目标不存在：$originalTarget。"
            } elseif ($stemMap[$leaf].Count -gt 1) {
                Add-Finding 'warning' 'ambiguous-wikilink' $relativePath "链接目标不唯一：$originalTarget。"
            }
        }
    }

    $secretPattern = '(?im)(password|api[_-]?key|secret|token)\s*[:=]\s*["'']?[^\s`"'']{8,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY'
    if ($content -match $secretPattern) {
        Add-Finding 'error' 'possible-secret' $relativePath '发现疑似凭据赋值或私钥；请人工核查，输出已隐藏具体值。'
    }

    $noteRecords.Add([pscustomobject]@{
        Path = $relativePath
        Status = $status
        CoreLines = Get-CoreLines $parsed.Body
    }) | Out-Null
}

for ($i = 0; $i -lt $noteRecords.Count; $i++) {
    for ($j = $i + 1; $j -lt $noteRecords.Count; $j++) {
        $left = $noteRecords[$i]
        $right = $noteRecords[$j]
        if ($left.CoreLines.Count -eq 0 -or $right.CoreLines.Count -eq 0) {
            continue
        }

        $intersection = 0
        foreach ($line in $left.CoreLines) {
            if ($right.CoreLines.Contains($line)) {
                $intersection++
            }
        }
        $union = $left.CoreLines.Count + $right.CoreLines.Count - $intersection
        $score = $intersection / $union
        if ($score -ge $SimilarityThreshold) {
            Add-Finding 'warning' 'high-content-similarity' $left.Path ("与 {0} 的正文相似度为 {1:P0}，需要语义复核。" -f $right.Path, $score)
        }
    }
}

$indexPath = Join-Path $resolvedVault '90-System\Codex-Memory-Index.md'
if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
    Add-Finding 'warning' 'missing-index' '90-System\Codex-Memory-Index.md' '本地记忆索引不存在。'
} elseif ($formalFiles.Count -gt 0) {
    $newestFormal = $formalFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ((Get-Item -LiteralPath $indexPath).LastWriteTime -lt $newestFormal.LastWriteTime) {
        Add-Finding 'warning' 'stale-index' '90-System\Codex-Memory-Index.md' '索引早于最新正式记忆，请在清洗后重建。'
    }
}

$summary = [pscustomobject]@{
    vault = $resolvedVault
    formal_notes = $formalFiles.Count
    active = ($noteRecords | Where-Object Status -eq 'active' | Measure-Object).Count
    uncertain = ($noteRecords | Where-Object Status -eq 'uncertain' | Measure-Object).Count
    stale = ($noteRecords | Where-Object Status -eq 'stale' | Measure-Object).Count
    superseded = ($noteRecords | Where-Object Status -eq 'superseded' | Measure-Object).Count
    errors = ($Findings | Where-Object severity -eq 'error' | Measure-Object).Count
    warnings = ($Findings | Where-Object severity -eq 'warning' | Measure-Object).Count
    findings = $Findings.ToArray()
}

if ($Json) {
    $summary | ConvertTo-Json -Depth 6
} else {
    Write-Output ("正式记忆：{0}；active={1}，uncertain={2}，stale={3}，superseded={4}" -f $summary.formal_notes, $summary.active, $summary.uncertain, $summary.stale, $summary.superseded)
    Write-Output ("错误：{0}；警告：{1}" -f $summary.errors, $summary.warnings)
    foreach ($finding in $Findings) {
        Write-Output ("[{0}] {1} | {2} | {3}" -f $finding.severity.ToUpperInvariant(), $finding.code, $finding.path, $finding.message)
    }
}

if ($summary.errors -gt 0) {
    exit 1
}

exit 0
