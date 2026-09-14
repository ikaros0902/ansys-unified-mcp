$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceDir = Join-Path $RepoRoot "SKILLs"
$TargetKiro = Join-Path $RepoRoot ".kiro\skills"
$TargetGlobal = Join-Path $env:USERPROFILE ".gemini\config\skills"

if (Test-Path $SourceDir) {
    if (-not (Test-Path $TargetKiro)) { New-Item -ItemType Directory -Path $TargetKiro -Force | Out-Null }
    if (-not (Test-Path $TargetGlobal)) { New-Item -ItemType Directory -Path $TargetGlobal -Force | Out-Null }
    Copy-Item -Path "$SourceDir\*" -Destination $TargetKiro -Recurse -Force
    Copy-Item -Path "$SourceDir\*" -Destination $TargetGlobal -Recurse -Force
    Write-Host "Skills successfully synchronized to .kiro and global config ($TargetGlobal)!"
}
