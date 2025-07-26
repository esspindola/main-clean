@echo off
echo === REINICIO SIMPLE SIN REBUILD ===

echo 1. Verificando contenedores...
docker ps

echo 2. Copiando archivo corregido...
docker cp robust_multi_engine_ocr.py backend-ocr-ocr-backend-1:/app/robust_multi_engine_ocr.py
if %errorlevel% neq 0 (
    echo Intentando nombre alternativo...
    docker cp robust_multi_engine_ocr.py ocr-backend:/app/robust_multi_engine_ocr.py
)

echo 3. Reiniciando backend...
docker compose restart backend-ocr

echo 4. Verificando estado...
docker compose ps

echo === LISTO PARA PROBAR ===
echo Espera 10 segundos y ve a: http://localhost:8001/docs
pause