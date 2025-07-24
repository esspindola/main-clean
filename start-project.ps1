# Script para iniciar ZatoBox v2.0
# Autor: ZatoBox Team
# Versión: 2.0.0

Write-Host "🚀 Iniciando ZatoBox v2.0..." -ForegroundColor Green
Write-Host ""

# Verificar si Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detectado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no está instalado. Por favor instálalo desde https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Verificar si npm está instalado
try {
    $npmVersion = npm --version
    Write-Host "✅ npm detectado: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm no está instalado." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Detener procesos Node.js existentes
Write-Host "🛑 Deteniendo procesos Node.js existentes..." -ForegroundColor Yellow
try {
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ Procesos detenidos" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ No hay procesos Node.js ejecutándose" -ForegroundColor Blue
}

Write-Host ""

# Verificar si el puerto 4444 está libre
Write-Host "🔍 Verificando puerto 4444..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr ":4444" | findstr "LISTENING"
if ($portCheck) {
    Write-Host "⚠️ Puerto 4444 está en uso. Intentando liberarlo..." -ForegroundColor Yellow
    $processId = ($portCheck -split '\s+')[4]
    try {
        taskkill /PID $processId /F
        Write-Host "✅ Puerto 4444 liberado" -ForegroundColor Green
    } catch {
        Write-Host "❌ No se pudo liberar el puerto 4444" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Puerto 4444 está libre" -ForegroundColor Green
}

Write-Host ""

# Instalar dependencias si es necesario
Write-Host "📦 Verificando dependencias..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias del proyecto..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencias ya instaladas" -ForegroundColor Green
}

Write-Host ""

# Iniciar backend
Write-Host "🔧 Iniciando backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev:backend" -WindowStyle Normal
Write-Host "✅ Backend iniciado en http://localhost:4444" -ForegroundColor Green

# Esperar un momento para que el backend se inicie
Write-Host "⏳ Esperando que el backend se inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar que el backend esté funcionando
Write-Host "🔍 Verificando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4444/health" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend respondió con código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ No se pudo conectar al backend" -ForegroundColor Red
    Write-Host "Verifica que el backend se haya iniciado correctamente" -ForegroundColor Yellow
}

Write-Host ""

# Iniciar frontend
Write-Host "🎨 Iniciando frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev:frontend" -WindowStyle Normal
Write-Host "✅ Frontend iniciado en http://localhost:5173" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 ¡ZatoBox v2.0 iniciado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 URLs de acceso:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://localhost:4444" -ForegroundColor White
Write-Host "   Health:   http://localhost:4444/health" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Credenciales de prueba:" -ForegroundColor Cyan
Write-Host "   Email: admin@frontposw.com" -ForegroundColor White
Write-Host "   Password: admin12345678" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test CORS: Abre test-cors.html en tu navegador" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar este script..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 