@echo off
echo ==========================================
echo   REBUILD COMPLETO CON SISTEMA OPTIMIZADO
echo ==========================================
echo.

echo PROBLEMA IDENTIFICADO:
echo - Workers muriendo por timeout/memoria
echo - Sistema inteligente no se est■ cargando
echo - EasyOCR causando problemas de memoria
echo.

echo SOLUCI■N:
echo 1. Usar configuraci■n optimizada con l■mites de memoria
echo 2. Rebuild completo con c■digo inteligente incluido
echo 3. Configuraci■n Redis ultra liviana
echo.

echo ==========================================
echo 1. DETENIENDO SISTEMA ACTUAL...
echo ==========================================
docker compose down
docker system prune -f

echo.
echo ==========================================  
echo 2. APLICANDO CONFIGURACI■N OPTIMIZADA...
echo ==========================================

if exist docker-compose.optimized.yml (
    copy docker-compose.optimized.yml docker-compose.yml
    echo ✅ docker-compose.yml optimizado aplicado
) else (
    echo ❌ docker-compose.optimized.yml no encontrado
)

if exist nginx.optimized.conf (
    copy nginx.optimized.conf nginx.conf  
    echo ✅ nginx.conf optimizado aplicado
) else (
    echo ❌ nginx.optimized.conf no encontrado
)

echo.
echo ==========================================
echo 3. VERIFICANDO ARCHIVOS DEL SISTEMA INTELIGENTE...
echo ==========================================

if exist smart_invoice_nlp.py (
    echo ✅ smart_invoice_nlp.py - OK
) else (
    echo ❌ smart_invoice_nlp.py - FALTA - SISTEMA NO FUNCIONAR┴
)

if exist ultra_light_processor.py (
    echo ✅ ultra_light_processor.py - OK
) else (
    echo ❌ ultra_light_processor.py - FALTA - SISTEMA NO FUNCIONAR┴
)

if exist robust_multi_engine_ocr.py (
    echo ✅ robust_multi_engine_ocr.py - OK
) else (
    echo ❌ robust_multi_engine_ocr.py - FALTA - SISTEMA NO FUNCIONAR┴
)

echo.
echo ==========================================
echo 4. REBUILD COMPLETO CON OPTIMIZACIONES...
echo ==========================================
docker compose up -d --build --force-recreate

echo.
echo ==========================================
echo 5. ESPERANDO INICIO COMPLETO...
echo ==========================================
echo Esto puede tomar 2-3 minutos...
timeout /t 30 /nobreak

echo.
echo ==========================================
echo 6. VERIFICANDO LOGS DEL SISTEMA INTELIGENTE...
echo ==========================================
docker compose logs backend-ocr | findstr "PATTERN\|SMART\|NLP\|robusto\|TIMEOUT\|SIGKILL"

echo.
echo ==========================================
echo 7. VERIFICANDO ESTADO FINAL...
echo ==========================================
docker compose ps
echo.

echo Probando conexi■n...
curl -X GET http://localhost:8001/health

echo.
echo ==========================================
echo   REBUILD COMPLETADO
echo ==========================================
echo.
echo ✅ Si ves logs como:
echo    "PATTERN-ONLY MODE"
echo    "SMART NLP PATTERNS" 
echo    → Sistema inteligente ACTIVO
echo.
echo ❌ Si ves:  
echo    "WORKER TIMEOUT"
echo    "SIGKILL"
echo    → A·n hay problemas de memoria
echo.
echo 🔗 Prueba en: http://localhost:8001/docs
echo.
pause