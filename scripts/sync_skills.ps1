<#
.SYNOPSIS
同步 SKILLs 目錄到 .kiro/skills/

.DESCRIPTION
以 SKILLs/ 為 Single Source of Truth，將其內容同步至 .kiro/skills/。
若目標目錄不存在將自動建立。
#>

$SourceDir = "SKILLs"
$TargetDir = ".kiro\skills"

# 確保來源目錄存在
if (-not (Test-Path -Path $SourceDir)) {
    Write-Error "來源目錄 $SourceDir 不存在。"
    exit 1
}

# 確保目標目錄存在，不存在則建立
if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Write-Host "已建立目標目錄: $TargetDir"
}

# 執行同步拷貝，覆蓋目標
Write-Host "開始同步 $SourceDir 至 $TargetDir ..."
Copy-Item -Path "$SourceDir\*" -Destination $TargetDir -Recurse -Force

Write-Host "同步完成！摘要：已將 $SourceDir 的所有內容成功覆蓋至 $TargetDir。"
