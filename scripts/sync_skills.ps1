$SourceDir = "d:\Ikaros\ANSYS-unified-MCP\SKILLs"
$TargetKiro = "d:\Ikaros\ANSYS-unified-MCP\.kiro\skills"
$TargetGlobal = "C:\Users\4062863\.gemini\config\skills"

if (Test-Path $SourceDir) {
    Copy-Item -Path "$SourceDir\*" -Destination $TargetKiro -Recurse -Force
    Copy-Item -Path "$SourceDir\*" -Destination $TargetGlobal -Recurse -Force
    Write-Host "Skills successfully synchronized to .kiro and global config!"
}
