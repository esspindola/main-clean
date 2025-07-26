Write-Host "==========================================" -ForegroundColor Green
Write-Host "  DEPLOYING INTELLIGENT ALGORITHM SYSTEM" -ForegroundColor Green  
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""


Set-Location "C:\Users\aryes\Documents\ocr\backend-ocr"

Write-Host "1. Checking local files..." -ForegroundColor Yellow
$files = @(
    "smart_invoice_nlp.py",
    "ultra_light_processor.py", 
    "robust_multi_engine_ocr.py",
    "app\core\ml_models.py"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file - EXISTS" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - MISSING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "2. Copying files to container..." -ForegroundColor Yellow

# Try different Docker commands
$dockerCommands = @(
    "docker",
    "C:\Program Files\Docker\Docker\resources\bin\docker.exe",
    "C:\ProgramData\DockerDesktop\version-bin\docker.exe"
)

$dockerFound = $false
foreach ($dockerCmd in $dockerCommands) {
    try {
        & $dockerCmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Found Docker at: $dockerCmd" -ForegroundColor Green
            $docker = $dockerCmd
            $dockerFound = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $dockerFound) {
    Write-Host "❌ Docker not found in PATH. Please:" -ForegroundColor Red
    Write-Host "   1. Open Docker Desktop" -ForegroundColor Yellow
    Write-Host "   2. Run these commands manually:" -ForegroundColor Yellow
    Write-Host "      docker cp smart_invoice_nlp.py ocr-backend:/app/" -ForegroundColor Cyan
    Write-Host "      docker cp ultra_light_processor.py ocr-backend:/app/" -ForegroundColor Cyan
    Write-Host "      docker cp robust_multi_engine_ocr.py ocr-backend:/app/" -ForegroundColor Cyan
    Write-Host "      docker cp app\core\ml_models.py ocr-backend:/app/app/core/" -ForegroundColor Cyan
    Write-Host "      docker restart ocr-backend" -ForegroundColor Cyan
    pause
    exit 1
}

# Copy files
Write-Host "Copying smart_invoice_nlp.py..." -ForegroundColor Cyan
& $docker cp smart_invoice_nlp.py ocr-backend:/app/

Write-Host "Copying ultra_light_processor.py..." -ForegroundColor Cyan  
& $docker cp ultra_light_processor.py ocr-backend:/app/

Write-Host "Copying robust_multi_engine_ocr.py..." -ForegroundColor Cyan
& $docker cp robust_multi_engine_ocr.py ocr-backend:/app/

Write-Host "Copying optimized ml_models.py..." -ForegroundColor Cyan
& $docker cp app\core\ml_models.py ocr-backend:/app/app/core/

Write-Host ""
Write-Host "3. Verifying files in container..." -ForegroundColor Yellow
& $docker exec ocr-backend ls -la /app/ | Select-String "smart|ultra|robust"

Write-Host ""
Write-Host "4. Restarting container to apply changes..." -ForegroundColor Yellow
& $docker restart ocr-backend

Write-Host ""
Write-Host "5. Waiting for restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "6. Checking logs for intelligent system..." -ForegroundColor Yellow
Write-Host "Looking for: PATTERN-ONLY MODE, SMART NLP PATTERNS" -ForegroundColor Cyan
& $docker logs ocr-backend --tail 50 | Select-String "PATTERN|SMART|NLP|robusto"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETED" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Test the system at: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Expected logs should show:" -ForegroundColor Yellow
Write-Host "   - 'PATTERN-ONLY MODE: Skipping YOLO loading'" -ForegroundColor Cyan
Write-Host "   - 'SMART NLP PATTERNS loaded successfully'" -ForegroundColor Cyan
Write-Host ""
pause