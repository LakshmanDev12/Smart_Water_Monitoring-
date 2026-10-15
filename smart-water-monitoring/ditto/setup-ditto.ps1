# ============================================
# Eclipse Ditto Setup Script
# Creates digital twin policy and things for
# Smart Water Quality Monitoring
# ============================================

$DITTO_URL = "http://localhost:8085"
$MAX_RETRIES = 30
$RETRY_DELAY = 5

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Eclipse Ditto - Digital Twin Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Wait for Ditto to be healthy
Write-Host "[1/3] Waiting for Ditto to be ready..." -ForegroundColor Yellow
$retries = 0
$dittoReady = $false

while (-not $dittoReady -and $retries -lt $MAX_RETRIES) {
    try {
        $response = Invoke-RestMethod -Uri "$DITTO_URL/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
        if ($response) {
            $dittoReady = $true
            Write-Host "  Ditto is healthy!" -ForegroundColor Green
        }
    } catch {
        $retries++
        Write-Host "  Attempt $retries/$MAX_RETRIES - Ditto not ready yet. Retrying in ${RETRY_DELAY}s..." -ForegroundColor Gray
        Start-Sleep -Seconds $RETRY_DELAY
    }
}

if (-not $dittoReady) {
    Write-Host "  ERROR: Ditto did not become healthy after $MAX_RETRIES attempts." -ForegroundColor Red
    Write-Host "  Make sure Docker containers are running: docker compose ps" -ForegroundColor Red
    exit 1
}

# Step 2: Create Policy
Write-Host ""
Write-Host "[2/3] Creating tank policy..." -ForegroundColor Yellow

$policy = @{
    entries = @{
        DEFAULT = @{
            subjects = @{
                "nginx:ditto" = @{
                    type = "pre-authenticated connection"
                }
            }
            resources = @{
                "thing:/" = @{
                    grant = @("READ", "WRITE")
                    revoke = @()
                }
                "policy:/" = @{
                    grant = @("READ", "WRITE")
                    revoke = @()
                }
                "message:/" = @{
                    grant = @("READ", "WRITE")
                    revoke = @()
                }
            }
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $result = Invoke-RestMethod -Uri "$DITTO_URL/api/2/policies/water:tank-policy" -Method Put -Body $policy -ContentType "application/json" -ErrorAction Stop
    Write-Host "  Policy 'water:tank-policy' created successfully!" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    if ($statusCode -eq 409) {
        Write-Host "  Policy 'water:tank-policy' already exists (OK)." -ForegroundColor Cyan
    } else {
        Write-Host "  Warning: Policy creation returned status $statusCode" -ForegroundColor Yellow
        Write-Host "  $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Step 3: Create Things
Write-Host ""
Write-Host "[3/3] Creating digital twins..." -ForegroundColor Yellow

$tanks = @("TANK001", "TANK002", "TANK003")

foreach ($tankId in $tanks) {
    $thing = @{
        policyId = "water:tank-policy"
        attributes = @{
            tankId = $tankId
            description = "Smart Water Tank $tankId"
            location = "Plant Floor"
        }
        features = @{
            waterQuality = @{
                properties = @{
                    pH = 7.0
                    turbidity = 0.0
                    temperature = 25.0
                    waterLevel = 50.0
                    status = "UNKNOWN"
                    alerts = @()
                    timestamp = ""
                }
            }
        }
    } | ConvertTo-Json -Depth 10

    try {
        $result = Invoke-RestMethod -Uri "$DITTO_URL/api/2/things/water:$tankId" -Method Put -Body $thing -ContentType "application/json" -ErrorAction Stop
        Write-Host "  Digital twin 'water:$tankId' created successfully!" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        if ($statusCode -eq 409) {
            Write-Host "  Digital twin 'water:$tankId' already exists (OK)." -ForegroundColor Cyan
        } else {
            Write-Host "  Warning: Thing creation for $tankId returned status $statusCode" -ForegroundColor Yellow
            Write-Host "  $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Verify twins:" -ForegroundColor White
Write-Host "    curl http://localhost:8085/api/2/things/water:TANK001" -ForegroundColor Gray
Write-Host "    curl http://localhost:8085/api/2/things/water:TANK002" -ForegroundColor Gray
Write-Host "    curl http://localhost:8085/api/2/things/water:TANK003" -ForegroundColor Gray
Write-Host ""
