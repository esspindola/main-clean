@echo off
echo ========================================
echo   REBUILD SISTEMA OCR ULTRA LIGERO
echo ========================================
echo.
echo 🚀 Sin PyTorch, sin YOLO - Solo patrones inteligentes
echo 💾 Memoria máxima: 1GB
echo ⚡ Tiempo de inicio: ~15 segundos
echo.

echo 1. Deteniendo servicios anteriores...
docker-compose down 2>nul
docker-compose -f docker-compose.optimized.yml down 2>nul
docker-compose -f docker-compose-light.yml down 2>nul

echo.
echo 2. Limpiando imágenes antiguas...
docker rmi backend-ocr-backend-ocr 2>nul
docker rmi backend-ocr-ocr-backend 2>nul
docker rmi backend-ocr_ocr-backend 2>nul

echo.
echo 3. Construyendo imagen ultra ligera...
docker-compose -f docker-compose-light.yml build --no-cache

echo.
echo 4. Iniciando servicios...
docker-compose -f docker-compose-light.yml up -d

echo.
echo 5. Esperando que el servicio esté listo...
timeout /t 20 /nobreak > nul

echo.
echo 6. Verificando salud del servicio...
curl -X GET http://localhost:8001/health

echo.
echo 7. Probando endpoint de debug...
curl -X GET http://localhost:8001/api/v1/invoice/debug

echo.
echo ========================================
echo   SISTEMA LISTO
echo ========================================
echo.
echo ✅ URL: http://localhost:8001
echo 🔍 Health: http://localhost:8001/health  
echo 🧠 Debug: http://localhost:8001/api/v1/invoice/debug
echo 📝 Process: http://localhost:8001/api/v1/invoice/process
echo.
echo 📊 Para ver logs en tiempo real:
echo    docker logs -f ocr-backend-light
echo.
pause