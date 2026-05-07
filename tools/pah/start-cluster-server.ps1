#!/usr/bin/env pwsh
# tools/pah/start-cluster-server.ps1
#
# Launched by start_cluster_server.bat at the repo root. Brings up the full
# cluster-server side on this Windows machine: docker check, pub_key derive,
# controller container, viz HTTP/SSE.
#
# Idempotent: re-running picks up an already-running controller, just
# (re)starts the viz.

param(
    [int]    $VizPort = 7777,
    [int]    $ControllerPort = 12321,
    [string] $LanIp = "",
    [switch] $NoControllerRestart
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

Write-Host ""
Write-Host "==> melee p@h cluster server bootstrap" -ForegroundColor Cyan
Write-Host ""

# 1. Detect LAN IP if not passed.
if (-not $LanIp) {
    $candidates = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.InterfaceAlias -notmatch 'Loopback|vEthernet|WSL' -and
            $_.IPAddress -notmatch '^169\.|^127\.'
        } |
        Select-Object -ExpandProperty IPAddress
    # Prefer 192.168.* over 10.* over others.
    $LanIp = ($candidates | Where-Object { $_ -like "192.168.*" } | Select-Object -First 1)
    if (-not $LanIp) {
        $LanIp = ($candidates | Select-Object -First 1)
    }
    if (-not $LanIp) {
        throw "Could not detect a LAN IP. Pass -LanIp 192.168.x.y explicitly."
    }
}
Write-Host "    LAN IP: $LanIp" -ForegroundColor Green

# 2. Verify Docker Desktop is running.
Write-Host "    checking Docker..." -NoNewline
try {
    & docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker info exit $LASTEXITCODE" }
    Write-Host " ok" -ForegroundColor Green
} catch {
    Write-Host " NOT RUNNING" -ForegroundColor Red
    Write-Host ""
    Write-Host "Open Docker Desktop from the Start menu, wait until the whale icon" -ForegroundColor Yellow
    Write-Host "in the tray says 'Engine running', then re-run this script." -ForegroundColor Yellow
    exit 2
}

# 3. Cache controller pub_key if not already done; write controller_address.
$cfgPath = Join-Path $RepoRoot "build-linux\pah-controller-state\pah_config.toml"
if (Test-Path $cfgPath) {
    $hasPub = Select-String -Path $cfgPath -Pattern '^pub_key' -Quiet
    if (-not $hasPub) {
        Write-Host "    deriving pub_key..." -NoNewline
        & python tools/pah/derive-pubkey.py
        if ($LASTEXITCODE -ne 0) { throw "derive-pubkey.py failed" }
        Write-Host " done" -ForegroundColor Green
    } else {
        Write-Host "    pub_key already cached" -ForegroundColor Green
    }
    # Write/overwrite controller_address so /kit/info doesn't have to fall back
    # to the request Host header. Workers fetching /kit/pah.conf will then get
    # the right server_address regardless of how the viz is launched.
    $cfgText = Get-Content $cfgPath -Raw
    $newAddr = "${LanIp}:${ControllerPort}"
    if ($cfgText -match '(?m)^controller_address\s*=') {
        $cfgText = ($cfgText -replace '(?m)^controller_address\s*=.*$', "controller_address = `"$newAddr`"")
    } else {
        $cfgText = $cfgText.TrimEnd() + "`ncontroller_address = `"$newAddr`"`n"
    }
    Set-Content -Path $cfgPath -Value $cfgText -NoNewline -Encoding ASCII
    Write-Host "    controller_address = $newAddr" -ForegroundColor Green
} else {
    Write-Host "    no pah_config.toml yet — controller will create on first start" -ForegroundColor DarkYellow
}

# 4. Start the controller container (detached) unless told otherwise.
$running = & docker ps --filter "name=melee-pah-controller" --format "{{.Names}}" 2>$null
if ($running -eq "melee-pah-controller") {
    Write-Host "    controller already running" -ForegroundColor Green
} elseif ($NoControllerRestart) {
    Write-Host "    controller not running and -NoControllerRestart set — skipping" -ForegroundColor DarkYellow
} else {
    Write-Host "    starting controller on port $ControllerPort..."
    $startScript = Join-Path $RepoRoot "build-linux\pah-worker-kit\tools\pah\start-controller.ps1"
    if (-not (Test-Path $startScript)) {
        throw "start-controller.ps1 not found at $startScript"
    }
    # Remove any stale stopped container first so the rerun is clean.
    $stale = & docker ps -a --filter "name=melee-pah-controller" --format "{{.Names}}" 2>$null
    if ($stale -eq "melee-pah-controller") {
        & docker rm -f melee-pah-controller 2>&1 | Out-Null
    }
    & $startScript -Port $ControllerPort -Detach
    if ($LASTEXITCODE -ne 0) { throw "start-controller.ps1 exit $LASTEXITCODE" }
    Write-Host "    controller started" -ForegroundColor Green
}

# 5. Print the worker URLs and start the viz.
$kitBase = "http://${LanIp}:$VizPort/kit"
Write-Host ""
Write-Host "==> ready" -ForegroundColor Cyan
Write-Host ""
Write-Host "    viz:        http://${LanIp}:$VizPort/" -ForegroundColor White
Write-Host "    controller: ${LanIp}:$ControllerPort"   -ForegroundColor White
Write-Host ""
Write-Host "    worker bootstrap (mac/linux):" -ForegroundColor Cyan
Write-Host "      CONTROLLER_URL=http://${LanIp}:$VizPort \" -ForegroundColor Gray
Write-Host "        curl -fsSL $kitBase/setup-worker.sh | bash" -ForegroundColor Gray
Write-Host ""
Write-Host "    worker bootstrap (windows):" -ForegroundColor Cyan
Write-Host "      iwr $kitBase/bootstrap-worker.ps1 -OutFile `$env:TEMP\bs.ps1" -ForegroundColor Gray
Write-Host "      & `$env:TEMP\bs.ps1 -KitUrl $kitBase/pah-worker-kit.zip -InstallPrereqs" -ForegroundColor Gray
Write-Host ""
Write-Host "    starting viz... ctrl-c to stop (controller keeps running)" -ForegroundColor Cyan
Write-Host ""

$env:PAH_CONTROLLER_HOST = $LanIp
$env:PAH_CONTROLLER_PORT = "$ControllerPort"
$env:VIZ_PORT = "$VizPort"

# Foreground exec — user sees viz logs and ctrl-c stops it cleanly.
& python tools/viz/serve.py
exit $LASTEXITCODE
