

Write-Host "🚀 Starting Complete OCR System..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green


Write-Host "📦 Starting Node.js Backend (port 4444)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; npm start" -WindowStyle Normal

Start-Sleep -Seconds 3


Write-Host "🧠 Starting Python OCR Backend (port 5000)..." -ForegroundColor Yellow
$ocrPath = "C:\Users\aryes\Documents\ocr\backend-ocr"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ocrPath'; python run.py" -WindowStyle Normal

Start-Sleep -Seconds 5

# Start the React frontend (port 5173)
Write-Host "🌐 Starting React Frontend (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ System Starting!" -ForegroundColor Green
Write-Host "📝 Services:" -ForegroundColor Cyan
Write-Host "   • Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "   • Node Backend: http://localhost:4444" -ForegroundColor White
Write-Host "   • OCR Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "   • OCR Swagger:  http://localhost:5000/docs/" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Wait a few seconds for all services to start..." -ForegroundColor Yellow
Write-Host "🔧 Check each window for startup logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this script (services will continue running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")