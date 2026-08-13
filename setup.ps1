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
# 6. Configure SpaceClaim Auto gRPC Startup
Write-Host ""
Write-Host "[6/6] Configuring SpaceClaim Auto gRPC Startup..." -ForegroundColor Cyan

# Use the detected ANSYS versions
if ($ansysVersions.Count -eq 0) {
    Write-Host "ERROR: No ANSYS versions detected. Cannot configure SpaceClaim gRPC." -ForegroundColor Red
    exit 1
}

# Use the first (or latest) detected version
$primaryVersion = $ansysVersions[0]
$scAddinsPath = "$env:ProgramData\SpaceClaim\AddIns"
if (-Not (Test-Path $scAddinsPath)) {
    New-Item -ItemType Directory -Force -Path $scAddinsPath | Out-Null
}

# Resolve the actual ANSYS install root instead of assuming the default
# "C:\Program Files\ANSYS Inc" location. Priority: AWP_ROOT<ver> env var
# (set by the ANSYS installer itself, always correct) -> registry InstallDir
# -> standard-location fallbacks.
$installRoot = $null
$awpRootVar = "AWP_ROOT$primaryVersion"
$awpRootValue = [Environment]::GetEnvironmentVariable($awpRootVar, "Machine")
if ($awpRootValue -and (Test-Path $awpRootValue)) {
    $installRoot = $awpRootValue
} else {
    $regKey = "HKLM:\SOFTWARE\ANSYS, Inc.\ANSYS\$primaryVersion"
    if (Test-Path $regKey) {
        $regInstallDir = (Get-ItemProperty -Path $regKey -ErrorAction SilentlyContinue).InstallDir
        if ($regInstallDir -and (Test-Path $regInstallDir)) {
            $installRoot = $regInstallDir
        }
    }
}
if (-Not $installRoot) {
    foreach ($base in @("C:\Program Files\ANSYS Inc", "D:\ANSYS Inc")) {
        $candidate = Join-Path $base "v$primaryVersion"
        if (Test-Path $candidate) {
            $installRoot = $candidate
            break
        }
    }
}

if (-Not $installRoot) {
    Write-Host "WARNING: Could not resolve ANSYS v$primaryVersion install root (checked $awpRootVar, registry, and standard locations). Skipping SpaceClaim gRPC config." -ForegroundColor Yellow
    $assemblyPath = $null
} else {
    $assemblyPath = Join-Path $installRoot "Addins\ApiServer\Presentation.ApiServerAddIn.dll"
}

if (-Not $assemblyPath -or -Not (Test-Path $assemblyPath)) {
    Write-Host "WARNING: ApiServer DLL not found at $assemblyPath. Skipping SpaceClaim gRPC config." -ForegroundColor Yellow
} else {
    $manifestPath = Join-Path $scAddinsPath "ApiServerAddIn.Manifest.xml"
    $manifestContent = @"
<?xml version="1.0" encoding="utf-8" ?>
<!-- Auto-configured by ANSYS Unified MCP Server Setup for v$primaryVersion -->
<AddIns>
  <AddIn name="Discovery Api Server"
         description="Discovery remote API server."
         assembly="$assemblyPath"
         typename="Presentation.ApiServerAddIn.ApiServerAddIn"
         host="SameAppDomain"/>
</AddIns>
"@

    Set-Content -Path $manifestPath -Value $manifestContent -Encoding UTF8
    Write-Host "Configured SpaceClaim auto gRPC (v$primaryVersion) at: $manifestPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Setup Completed Successfully!" -ForegroundColor Green
Write-Host "SpaceClaim gRPC server will auto-start whenever SpaceClaim opens (on port 50051)." -ForegroundColor Green
Write-Host "AI can connect to SpaceClaim at any time without interrupting your work!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan

