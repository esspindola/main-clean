@echo off
echo ========================================
echo   REBUILD SISTEMA OCR MEJORADO
echo ========================================
echo.
echo 🔧 Versión mejorada - Arregla valores null
echo 💾 Mejor manejo de errores y PDFs
echo ⚡ Múltiples configuraciones de OCR
echo.

echo 1. Deteniendo contenedor actual...
docker-compose -f docker-compose-light.yml down

echo.
echo 2. Limpiando imagen anterior...
docker rmi backend-ocr_ocr-backend 2>nul

echo.
echo 3. Construyendo imagen mejorada...
docker-compose -f docker-compose-light.yml build --no-cache

echo.
echo 4. Iniciando servicio mejorado...
docker-compose -f docker-compose-light.yml up -d

echo.
echo 5. Esperando que esté listo...
timeout /t 15 /nobreak > nul

echo.
echo 6. Verificando salud...
curl -X GET http://localhost:8001/health

echo.
echo 7. Probando debug...
curl -X GET http://localhost:8001/api/v1/invoice/debug

echo.
echo ========================================
echo   SISTEMA MEJORADO LISTO
echo ========================================
echo.
echo ✅ URL: http://localhost:8001
echo 🔧 Versión: IMPROVED
echo 📝 Frontend: http://localhost:5173/ocr-result
echo.
pause