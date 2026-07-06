param(
  [string]$Python = ""
)

$SkillRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $SkillRoot "..\..")
$PythonLauncher = Join-Path $RepoRoot "scripts\run-python.ps1"
$Dependencies = Join-Path $SkillRoot "dependencies"
$Wheels = Join-Path $Dependencies "python-wheels"
$Requirements = Join-Path $Dependencies "requirements-offline.txt"

if (-not (Test-Path $PythonLauncher)) {
  throw "Missing prerequisite: repository Python launcher not found: $PythonLauncher"
}
if (-not (Test-Path $Wheels)) {
  throw "Missing prerequisite: offline wheel directory not found: $Wheels"
}
if (-not (Test-Path $Requirements)) {
  throw "Missing prerequisite: offline requirements file not found: $Requirements"
}

$PreviousPython = $env:SKILLS_MANAGER_PYTHON
try {
  if (-not [string]::IsNullOrWhiteSpace($Python)) {
    $env:SKILLS_MANAGER_PYTHON = $Python
  }

  & $PythonLauncher -m pip install --no-index --find-links $Wheels -r $Requirements
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  & $PythonLauncher -c "import oracledb; print('oracledb', oracledb.__version__)"
} finally {
  $env:SKILLS_MANAGER_PYTHON = $PreviousPython
}
