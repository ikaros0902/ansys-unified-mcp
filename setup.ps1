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
Write-Host "[5/6] Generating MCP Client Config..."
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
# 6. Deploy SpaceClaimMCP ACT Extension (auto-starts gRPC on SpaceClaim launch)
Write-Host ""
Write-Host "[6/6] Deploying SpaceClaimMCP ACT Extension..." -ForegroundColor Cyan

$scPluginSource = Join-Path $ScriptDir "spaceclaim_plugin"

foreach ($ver in $ansysVersions) {
    $actExtDir = "$env:APPDATA\Ansys\v$ver\ACT\extensions"
    if (-Not (Test-Path $actExtDir)) {
        New-Item -ItemType Directory -Force -Path $actExtDir | Out-Null
    }

    # 部署擴充套件資料夾
    $scPluginTarget = Join-Path $actExtDir "SpaceClaimMCP"
    if (Test-Path $scPluginTarget) { Remove-Item -Recurse -Force $scPluginTarget }
    Copy-Item -Path $scPluginSource -Destination $scPluginTarget -Recurse
    Copy-Item -Path (Join-Path $scPluginSource "SpaceClaimMCP.xml") -Destination $actExtDir -Force
    Write-Host "Installed SpaceClaimMCP ACT Extension to: $actExtDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Setup Completed Successfully!" -ForegroundColor Green
Write-Host "SpaceClaim gRPC server will auto-start whenever SpaceClaim opens." -ForegroundColor Green
Write-Host "AI can connect to SpaceClaim at any time without interrupting your work!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan

