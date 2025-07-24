# Script para detener ZatoBox v2.0
# Autor: ZatoBox Team
# Versión: 2.0.0

Write-Host "🛑 Deteniendo ZatoBox v2.0..." -ForegroundColor Yellow
Write-Host ""

# Detener procesos Node.js
Write-Host "🔍 Buscando procesos Node.js..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    Write-Host "📋 Procesos Node.js encontrados:" -ForegroundColor Cyan
    $nodeProcesses | ForEach-Object {
        Write-Host "   PID: $($_.Id) - Memoria: $([math]::Round($_.WorkingSet64/1MB, 2)) MB" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "🛑 Deteniendo procesos..." -ForegroundColor Yellow
    try {
        $nodeProcesses | Stop-Process -Force
        Write-Host "✅ Todos los procesos Node.js detenidos" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al detener algunos procesos" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️ No hay procesos Node.js ejecutándose" -ForegroundColor Blue
}

Write-Host ""

# Verificar puertos
Write-Host "🔍 Verificando puertos..." -ForegroundColor Yellow

# Puerto 4444 (Backend)
$port4444 = netstat -ano | findstr ":4444" | findstr "LISTENING"
if ($port4444) {
    Write-Host "⚠️ Puerto 4444 aún está en uso" -ForegroundColor Yellow
    $processId = ($port4444 -split '\s+')[4]
    try {
        taskkill /PID $processId /F
        Write-Host "✅ Puerto 4444 liberado" -ForegroundColor Green
    } catch {
        Write-Host "❌ No se pudo liberar el puerto 4444" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Puerto 4444 está libre" -ForegroundColor Green
}

# Puerto 5173 (Frontend)
$port5173 = netstat -ano | findstr ":5173" | findstr "LISTENING"
if ($port5173) {
    Write-Host "⚠️ Puerto 5173 aún está en uso" -ForegroundColor Yellow
    $processId = ($port5173 -split '\s+')[4]
    try {
        taskkill /PID $processId /F
        Write-Host "✅ Puerto 5173 liberado" -ForegroundColor Green
    } catch {
        Write-Host "❌ No se pudo liberar el puerto 5173" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Puerto 5173 está libre" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 ¡ZatoBox v2.0 detenido exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Para reiniciar el proyecto, ejecuta: .\start-project.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 