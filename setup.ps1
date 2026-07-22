# ANSYS Unified MCP Server Setup Script

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ANSYS Unified MCP Server v2.0 Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/5] Checking Python environment..."
$pythonExe = "python"
try {
    $pythonVer = & $pythonExe --version 2>&1
    Write-Host "Found Python: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Ensure Python >= 3.10 is installed and in PATH." -ForegroundColor Red
    exit 1
}

# 2. Virtualenv
Write-Host "[2/5] Setting up virtual environment..."
$venvDir = Join-Path $ScriptDir ".venv"
if (-Not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment (.venv)..."
    & $pythonExe -m venv $venvDir
}

$pipExe = Join-Path $venvDir "Scripts\pip.exe"
$pythonVenvExe = Join-Path $venvDir "Scripts\python.exe"

Write-Host "Installing dependencies..."
& $pythonVenvExe -m pip install --upgrade pip setuptools wheel
& $pipExe install -e $ScriptDir

# 3. Detect ANSYS
Write-Host "[3/5] Detecting ANSYS installations..."
$ansysVersions = @()
$registryPath = "HKLM:\SOFTWARE\ANSYS, Inc.\ANSYS"
if (Test-Path $registryPath) {
    $keys = Get-ChildItem -Path $registryPath
    foreach ($key in $keys) {
        $ver = $key.PSChildName
        if ($ver -match "^\d+$") {
            $ansysVersions += $ver
            Write-Host "Found ANSYS version: v$ver" -ForegroundColor Green
        }
    }
}

if ($ansysVersions.Count -eq 0) {
    Write-Host "Warning: No ANSYS registry key found. Fallback to v251." -ForegroundColor Yellow
    $ansysVersions += "251"
}

# 4. Deploy ACT Plugin
Write-Host "[4/5] Deploying ACT Plugin & Hooks..."
$pluginSource = Join-Path $ScriptDir "workbench_plugin"
foreach ($ver in $ansysVersions) {
    $targetDir = "$env:APPDATA\Ansys\v$ver\ACT\extensions"
    
    if (-Not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    }
    
    $pluginTarget = Join-Path $targetDir "WorkbenchMCP"
    if (Test-Path $pluginTarget) {
        Remove-Item -Recurse -Force $pluginTarget
    }
    
    Copy-Item -Path $pluginSource -Destination $pluginTarget -Recurse
    Copy-Item -Path (Join-Path $pluginSource "WorkbenchMCP.xml") -Destination $targetDir -Force
    Write-Host "Installed ACT Plugin to: $targetDir" -ForegroundColor Green
}

# 5. Generate MCP Config
Write-Host "[5/5] Generating MCP Client Config..."
$mcpConfigPath = Join-Path $ScriptDir "mcp_config.json"

$configObject = @{
    mcpServers = @{
        "ansys-unified-mcp" = @{
            command = $pythonVenvExe
            args = @("-m", "ansys_unified_mcp.__main__")
            env = @{
                PYTHONUTF8 = "1"
            }
        }
    }
}

$configJson = $configObject | ConvertTo-Json -Depth 5
Set-Content -Path $mcpConfigPath -Value $configJson -Encoding UTF8
Write-Host "Generated config file: $mcpConfigPath" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Completed Successfully!" -ForegroundColor Green
Write-Host "You can now load mcp_config.json into your MCP client (Claude/Cursor)." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
