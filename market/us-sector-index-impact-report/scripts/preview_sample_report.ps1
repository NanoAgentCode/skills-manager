param(
  [string]$Output = "",
  [switch]$Open
)

$ErrorActionPreference = "Stop"

$SkillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$RepoRoot = Split-Path -Parent (Split-Path -Parent $SkillRoot)
$Input = Join-Path $SkillRoot "fixtures\sample-report.json"
$Renderer = Join-Path $SkillRoot "scripts\render_investment_bank_html.py"
$Launcher = Join-Path $RepoRoot "scripts\run-python.ps1"

if ([string]::IsNullOrWhiteSpace($Output)) {
  $Output = Join-Path $RepoRoot "output\us-sector-index-impact-report-sample.html"
}

& $Launcher $Renderer --input $Input --output $Output

$ResolvedOutput = Resolve-Path $Output
Write-Host "Preview report: $ResolvedOutput"

if ($Open) {
  Start-Process $ResolvedOutput
}
