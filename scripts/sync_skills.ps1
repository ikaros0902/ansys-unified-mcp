$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceDir = Join-Path $RepoRoot "SKILLs"
$TargetGlobal = Join-Path $env:USERPROFILE ".gemini\config\skills"

if (Test-Path $SourceDir) {
    # Ensure local directory junctions are configured (.kiro/skills, .cline/skills)
    $SetupScript = Join-Path $ScriptDir "setup_skill_junctions.py"
    if (Test-Path $SetupScript) {
        & python $SetupScript | Out-Null
    }

    if (-not (Test-Path $TargetGlobal)) { New-Item -ItemType Directory -Path $TargetGlobal -Force | Out-Null }
    Copy-Item -Path "$SourceDir\*" -Destination $TargetGlobal -Recurse -Force
    Write-Host "Skills successfully synchronized to global config ($TargetGlobal)!"
}
