@echo off
echo ==========================================
echo   VERIFICACIÓN Y APLICACIÓN INMEDIATA
echo ==========================================

echo.
echo 1. Verificando archivos locales...
if exist smart_invoice_nlp.py (
    echo ✅ smart_invoice_nlp.py - OK
) else (
    echo ❌ smart_invoice_nlp.py - FALTA
)

if exist ultra_light_processor.py (
    echo ✅ ultra_light_processor.py - OK
) else (
    echo ❌ ultra_light_processor.py - FALTA
)

if exist app\core\ml_models.py (
    echo ✅ app\core\ml_models.py - OK
) else (
    echo ❌ app\core\ml_models.py - FALTA
)

echo.
echo 2. Copiando archivos al contenedor activo...

echo Copiando sistema inteligente...
docker cp smart_invoice_nlp.py backend-ocr-ocr-backend-1:/app/smart_invoice_nlp.py
if %errorlevel% neq 0 (
    docker cp smart_invoice_nlp.py ocr-backend:/app/smart_invoice_nlp.py
)

echo Copiando procesador ultra liviano...
docker cp ultra_light_processor.py backend-ocr-ocr-backend-1:/app/ultra_light_processor.py
if %errorlevel% neq 0 (
    docker cp ultra_light_processor.py ocr-backend:/app/ultra_light_processor.py
)

echo Copiando sistema robusto actualizado...
docker cp robust_multi_engine_ocr.py backend-ocr-ocr-backend-1:/app/robust_multi_engine_ocr.py
if %errorlevel% neq 0 (
    docker cp robust_multi_engine_ocr.py ocr-backend:/app/robust_multi_engine_ocr.py
)

echo Copiando modelo optimizado...
docker cp app\core\ml_models.py backend-ocr-ocr-backend-1:/app/app/core/ml_models.py
if %errorlevel% neq 0 (
    docker cp app\core\ml_models.py ocr-backend:/app/app/core/ml_models.py
)

echo.
echo 3. Verificando archivos en el contenedor...
echo Archivos en /app:
docker exec backend-ocr-ocr-backend-1 ls -la /app/ | findstr "smart\|ultra\|robust"
if %errorlevel% neq 0 (
    docker exec ocr-backend ls -la /app/ | findstr "smart\|ultra\|robust"
)

echo.
echo 4. Reiniciando backend para aplicar cambios...
docker compose restart backend-ocr

echo.
echo 5. Esperando reinicio...
timeout /t 10 /nobreak

echo.
echo 6. Verificando logs del sistema inteligente...
echo Buscando logs de: "PATTERN-ONLY MODE" y "SMART NLP"
docker compose logs backend-ocr | findstr "PATTERN\|SMART\|NLP\|robusto"

echo.
echo ==========================================
echo   VERIFICACIÓN COMPLETADA
echo ==========================================
echo.
echo ✅ Si ves logs como:
echo    "PATTERN-ONLY MODE" 
echo    "SMART NLP PATTERNS"
echo    → Sistema inteligente ACTIVO
echo.
echo ❌ Si no ves esos logs:
echo    → Archivos no se copiaron correctamente
echo.
echo 🔗 Prueba en: http://localhost:8001/docs
echo.
pause