param(
    [Parameter(Mandatory = $true)]
    [string]$InputMarkdown,

    [Parameter(Mandatory = $true)]
    [string]$OutputHtml
)

$ErrorActionPreference = "Stop"

$markmap = Get-Command markmap -ErrorAction SilentlyContinue
if (-not $markmap) {
    throw "markmap command not found. Install with: npm install -g markmap-cli"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillDir = Split-Path -Parent $scriptDir
$sourceAssetsDir = Join-Path $skillDir "assets\markmap"

if (-not (Test-Path -LiteralPath $sourceAssetsDir)) {
    throw "Missing bundled markmap assets: $sourceAssetsDir"
}

$inputPath = (Resolve-Path -LiteralPath $InputMarkdown).Path
$outputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputHtml)
$outputDir = Split-Path -Parent $outputPath
if (-not $outputDir) {
    $outputDir = (Get-Location).Path
    $outputPath = Join-Path $outputDir $OutputHtml
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

& $markmap.Source $inputPath --output $outputPath --no-open
if ($LASTEXITCODE -ne 0) {
    throw "markmap failed with exit code $LASTEXITCODE"
}

$targetAssetsDir = Join-Path $outputDir "markmap-assets"
New-Item -ItemType Directory -Force -Path $targetAssetsDir | Out-Null

Copy-Item -LiteralPath (Join-Path $sourceAssetsDir "d3.min.js") -Destination (Join-Path $targetAssetsDir "d3.min.js") -Force
Copy-Item -LiteralPath (Join-Path $sourceAssetsDir "markmap-view.js") -Destination (Join-Path $targetAssetsDir "markmap-view.js") -Force
Copy-Item -LiteralPath (Join-Path $sourceAssetsDir "markmap-toolbar.js") -Destination (Join-Path $targetAssetsDir "markmap-toolbar.js") -Force
Copy-Item -LiteralPath (Join-Path $sourceAssetsDir "markmap-toolbar.css") -Destination (Join-Path $targetAssetsDir "markmap-toolbar.css") -Force

$html = Get-Content -LiteralPath $outputPath -Raw -Encoding UTF8
$html = $html -replace 'https?://cdn\.jsdelivr\.net/npm/d3@[^/]+/dist/d3(?:\.min)?\.js', './markmap-assets/d3.min.js'
$html = $html -replace 'https?://cdn\.jsdelivr\.net/npm/markmap-view@[^/]+/dist/browser/index\.js', './markmap-assets/markmap-view.js'
$html = $html -replace 'https?://cdn\.jsdelivr\.net/npm/markmap-toolbar@[^/]+/dist/index\.js', './markmap-assets/markmap-toolbar.js'
$html = $html -replace 'https?://cdn\.jsdelivr\.net/npm/markmap-toolbar@[^/]+/dist/style\.css', './markmap-assets/markmap-toolbar.css'
if ($html -match 'https?://[^"''\s>]+') {
    throw "Generated HTML still contains an external URL. The installed markmap-cli output is not compatible with the bundled offline assets."
}
Set-Content -LiteralPath $outputPath -Value $html -Encoding UTF8

Write-Output $outputPath
