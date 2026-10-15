# ============================================================
# Smart Water Quality Monitoring - Master Setup & Startup Script
# ============================================================

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SMART WATER QUALITY MONITORING AND DIGITAL TWIN SYSTEM    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/5] Checking Docker daemon status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker is not running! Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Docker Desktop is running." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker command failed. Ensure Docker Desktop is installed and running." -ForegroundColor Red
    exit 1
}

# Step 2: Build & Start Docker Stack
Write-Host ""
Write-Host "[2/5] Building and launching Docker Compose containers..." -ForegroundColor Yellow
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start Docker containers." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] All containers launched successfully." -ForegroundColor Green

# Step 3: Wait for Core Services Health
Write-Host ""
Write-Host "[3/5] Waiting for services to initialize..." -ForegroundColor Yellow

$maxWait = 60
$elapsed = 0
while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds 5
    $elapsed += 5
    Write-Host "  Waiting... ($elapsed/$maxWait seconds elapsed)" -ForegroundColor Gray
    
    try {
        $dittoCheck = Invoke-RestMethod -Uri "http://localhost:8085/health" -Method Get -ErrorAction SilentlyContinue
        if ($dittoCheck) {
            Write-Host "  [OK] Eclipse Ditto is healthy and ready!" -ForegroundColor Green
            break
        }
    } catch {
        # Continue waiting
    }
}

# Step 4: Provision Eclipse Ditto Digital Twins
Write-Host ""
Write-Host "[4/5] Provisioning Eclipse Ditto Digital Twins and Policies..." -ForegroundColor Yellow
if (Test-Path ".\ditto\setup-ditto.ps1") {
    & ".\ditto\setup-ditto.ps1"
} else {
    Write-Host "[WARNING] .\ditto\setup-ditto.ps1 not found. Skipping Ditto auto-provisioning." -ForegroundColor Yellow
}

# Step 5: Summary & Dashboard URLs
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SMART WATER QUALITY MONITORING - ECLIPSE IOFOG EDGE EDITION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Service Endpoints and Dashboards:" -ForegroundColor White
Write-Host "     -------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "     Grafana Dashboard : http://localhost:3000/d/water-quality-dashboard" -ForegroundColor Cyan
Write-Host "                         (User: admin | Pass: admin)" -ForegroundColor Gray
Write-Host "     ioFog Edge Engine : Running (Container: iofog-edge-processor)" -ForegroundColor Green
Write-Host "     InfluxDB UI        : http://localhost:8086" -ForegroundColor Cyan
Write-Host "                         (User: admin | Pass: adminpassword123)" -ForegroundColor Gray
Write-Host "     Eclipse Ditto API  : http://localhost:8085/api/2/things" -ForegroundColor Cyan
Write-Host "     Mosquitto Broker   : localhost:1883 (MQTT)" -ForegroundColor Cyan
Write-Host "     -------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Telemetry for TANK001, TANK002, TANK003 is automatically publishing every 5 seconds." -ForegroundColor White
Write-Host "To view live simulator logs, run: docker compose logs -f simulator" -ForegroundColor Gray
Write-Host ""
