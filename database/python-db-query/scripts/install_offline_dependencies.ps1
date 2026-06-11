param(
  [string]$Python = "python"
)

$SkillRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dependencies = Join-Path $SkillRoot "dependencies"
$Wheels = Join-Path $Dependencies "python-wheels"
$Requirements = Join-Path $Dependencies "requirements-offline.txt"

if (-not (Test-Path $Wheels)) {
  throw "Wheel directory not found: $Wheels"
}
if (-not (Test-Path $Requirements)) {
  throw "Requirements file not found: $Requirements"
}

& $Python -m pip install --no-index --find-links $Wheels -r $Requirements
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

& $Python -c "import oracledb; print('oracledb', oracledb.__version__)"
