$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$SourceDir = if (Test-Path (Join-Path $RepoRoot "skills")) { Join-Path $RepoRoot "skills" } else { Join-Path $RepoRoot "SKILLs" }
$TargetGlobal = Join-Path $env:USERPROFILE ".gemini\config\skills"

if (Test-Path $SourceDir) {
    # Ensure local directory junctions are configured (.kiro/skills, .cline/skills, .agents/skills)
    $SetupScript = Join-Path $ScriptDir "setup_skill_junctions.py"
    if (Test-Path $SetupScript) {
        $PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $PythonExe)) { $PythonExe = "python" }
        & $PythonExe $SetupScript | Out-Null
    }

    if (-not (Test-Path $TargetGlobal)) { New-Item -ItemType Directory -Path $TargetGlobal -Force | Out-Null }
    Copy-Item -Path "$SourceDir\*" -Destination $TargetGlobal -Recurse -Force
    Write-Host "Skills successfully synchronized to global config ($TargetGlobal)!"
}
