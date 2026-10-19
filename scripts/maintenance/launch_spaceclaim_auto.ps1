# 自動尋找空閒 Port 並啟動 SpaceClaim 的輔助腳本
#
# 路徑解析順序（與 src/ansys_unified_mcp/core/paths.py 的慣例一致，供非 Python
# 呼叫情境如本腳本沿用）：
# 1. 明確環境變數覆寫（ANSYS_SPACECLAIM_EXE）。
# 2. AWP_ROOT<ver> 環境變數（ANSYS 安裝程式本身會設定，優先信任）。
# 3. 標準安裝路徑的候選版本清單（與 start_api_server.py 的 _CANDIDATE_VERSIONS 一致）。

$ErrorActionPreference = "Stop"

$CandidateVersions = @("251", "252", "261", "242", "241")
$StandardRoots = @("C:\Program Files\ANSYS Inc", "D:\ANSYS Inc")

function Resolve-SpaceClaimExe {
    # 1. 明確環境變數覆寫
    if ($env:ANSYS_SPACECLAIM_EXE -and (Test-Path $env:ANSYS_SPACECLAIM_EXE)) {
        return $env:ANSYS_SPACECLAIM_EXE
    }

    # 2. AWP_ROOT<ver> 環境變數
    foreach ($ver in $CandidateVersions) {
        $awpRoot = [System.Environment]::GetEnvironmentVariable("AWP_ROOT$ver")
        if ($awpRoot) {
            $candidate = Join-Path $awpRoot "scdm\SpaceClaim.exe"
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    # 3. 標準安裝路徑候選版本
    foreach ($ver in $CandidateVersions) {
        foreach ($root in $StandardRoots) {
            $candidate = Join-Path $root "v$ver\scdm\SpaceClaim.exe"
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    return $null
}

function Find-FreePort {
    param([int]$StartPort = 50051)
    $port = $StartPort
    while ($true) {
        $sock = New-Object System.Net.Sockets.TcpClient
        try {
            $sock.Connect('127.0.0.1', $port)
            $sock.Close()
            $port++
        } catch {
            return $port
        }
    }
}

$spaceClaimExe = Resolve-SpaceClaimExe
if (-not $spaceClaimExe) {
    Write-Host "[MCP] 錯誤：找不到 SpaceClaim.exe。請設定 ANSYS_SPACECLAIM_EXE 環境變數，" -ForegroundColor Red
    Write-Host "[MCP] 或確認 AWP_ROOT<ver> 環境變數已正確設定（ANSYS 安裝程式應自動設定）。" -ForegroundColor Red
    exit 1
}

$port = Find-FreePort -StartPort 50051
Write-Host "[MCP] 啟動 SpaceClaim，分配 Port: $port" -ForegroundColor Green
Write-Host "[MCP] 使用執行檔：$spaceClaimExe" -ForegroundColor Green

$env:API_PORT = $port
Start-Process $spaceClaimExe
