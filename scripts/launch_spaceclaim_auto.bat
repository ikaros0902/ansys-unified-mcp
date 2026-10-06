@echo off
rem 自動尋找空閒 Port 並啟動 SpaceClaim（實際邏輯見同目錄下的 launch_spaceclaim_auto.ps1）
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_spaceclaim_auto.ps1"
