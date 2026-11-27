# Creates the ONE Python environment of the PCB thermal-warpage workflow (run once per PC):
# ODB Modifying Tool (step 2), LayerBuilder (step 3) and BGA-shadow leveling (step 9).
# The venv lives outside OneDrive on purpose (thousands of small files, sync conflicts).
#   powershell -ExecutionPolicy Bypass -File setup_env.ps1
param(
    [string]$Python = "",
    [string]$Venv = "$env:USERPROFILE\.venvs\pcb_thermal_warpage"
)
$ErrorActionPreference = "Stop"
if (-not $Python) {
    $cands = @("$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
               "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
               "py")
    foreach ($c in $cands) { if ($c -eq "py" -or (Test-Path $c)) { $Python = $c; break } }
}
Write-Host "Python: $Python"
if (-not (Test-Path "$Venv\Scripts\python.exe")) { & $Python -m venv $Venv }
& "$Venv\Scripts\python.exe" -m pip install --disable-pip-version-check --default-timeout 60 -r "$PSScriptRoot\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE). Check the network / proxy and run again." }
Write-Host ""
Write-Host "Done. Use this interpreter for every script of the workflow:"
Write-Host "  $Venv\Scripts\python.exe"
Write-Host "In VS Code: Python: Select Interpreter -> $Venv\Scripts\python.exe"
Write-Host "Self-test:  $Venv\Scripts\python.exe -m pytest `"$PSScriptRoot\tests`" -q"
