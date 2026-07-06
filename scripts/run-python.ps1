param(
  [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$PythonArgs
)

$ErrorActionPreference = "Stop"

function Add-Candidate {
  param(
    [System.Collections.Generic.List[string]]$Candidates,
    [string]$Path
  )

  if ([string]::IsNullOrWhiteSpace($Path)) {
    return
  }

  $expanded = [Environment]::ExpandEnvironmentVariables($Path.Trim('"'))
  if (-not $Candidates.Contains($expanded)) {
    $Candidates.Add($expanded)
  }
}

function Add-RegistryCandidates {
  param(
    [System.Collections.Generic.List[string]]$Candidates,
    [string]$Root
  )

  if (-not (Test-Path $Root)) {
    return
  }

  Get-ChildItem $Root -ErrorAction SilentlyContinue |
    Sort-Object PSChildName -Descending |
    ForEach-Object {
      $installPathKey = Join-Path $_.PSPath "InstallPath"
      if (Test-Path $installPathKey) {
        $key = Get-Item $installPathKey -ErrorAction SilentlyContinue
        $props = Get-ItemProperty $installPathKey -ErrorAction SilentlyContinue
        $defaultInstallPath = $key.GetValue("")
        Add-Candidate $Candidates $props.ExecutablePath
        if (-not [string]::IsNullOrWhiteSpace($defaultInstallPath)) {
          Add-Candidate $Candidates (Join-Path $defaultInstallPath "python.exe")
        }
      }
    }
}

function Resolve-Python {
  param([string]$RepoRoot)

  $candidates = [System.Collections.Generic.List[string]]::new()

  Add-Candidate $candidates $env:SKILLS_MANAGER_PYTHON
  Add-Candidate $candidates $env:PYTHON

  Add-Candidate $candidates (Join-Path $RepoRoot ".venv\Scripts\python.exe")
  Add-Candidate $candidates (Join-Path $RepoRoot "venv\Scripts\python.exe")

  Add-RegistryCandidates $candidates "HKCU:\Software\Python\PythonCore"
  Add-RegistryCandidates $candidates "HKLM:\SOFTWARE\Python\PythonCore"
  Add-RegistryCandidates $candidates "HKLM:\SOFTWARE\WOW6432Node\Python\PythonCore"

  foreach ($root in @($env:LOCALAPPDATA, $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
    if ([string]::IsNullOrWhiteSpace($root)) {
      continue
    }
    Get-ChildItem -Path $root -Directory -Filter "Python*" -ErrorAction SilentlyContinue |
      Sort-Object Name -Descending |
      ForEach-Object { Add-Candidate $candidates (Join-Path $_.FullName "python.exe") }
    Get-ChildItem -Path (Join-Path $root "Programs\Python") -Directory -Filter "Python*" -ErrorAction SilentlyContinue |
      Sort-Object Name -Descending |
      ForEach-Object { Add-Candidate $candidates (Join-Path $_.FullName "python.exe") }
  }

  Add-Candidate $candidates (Join-Path $env:WINDIR "py.exe")
  Add-Candidate $candidates (Join-Path $env:LOCALAPPDATA "Programs\Python\Launcher\py.exe")

  foreach ($candidate in $candidates) {
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
      continue
    }

    & $candidate -c "import sys; print(sys.executable)" *> $null
    if ($LASTEXITCODE -eq 0) {
      return $candidate
    }
  }

  $checked = ($candidates | Select-Object -Unique | ForEach-Object { "  - $_" }) -join [Environment]::NewLine
  throw @"
Missing prerequisite: Python interpreter not found.
Set SKILLS_MANAGER_PYTHON to a python.exe path, create .venv\Scripts\python.exe under the repository root, or install Python for Windows.
Checked:
$checked
"@
}

if (-not $PythonArgs -or $PythonArgs.Count -eq 0) {
  throw "Missing prerequisite: Python command arguments. Usage: .\scripts\run-python.ps1 <script.py|-m module> [args...]"
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Resolve-Python $RepoRoot

& $Python @PythonArgs
exit $LASTEXITCODE
