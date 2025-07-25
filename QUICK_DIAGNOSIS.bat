@echo off
echo ========================================
echo   DIAGN■STICO R┴PIDO DEL SISTEMA
echo ========================================
echo.

echo 1. Verificando archivos en el contenedor...
docker exec ocr-backend ls -la /app/ | findstr "smart\|ultra\|robust"

echo.
echo 2. Verificando si los archivos se importan correctamente...
docker exec ocr-backend python -c "
import sys
sys.path.append('/app')
try:
    import smart_invoice_nlp
    print('✅ smart_invoice_nlp.py - IMPORTA OK')
except Exception as e:
    print('❌ smart_invoice_nlp.py - ERROR:', e)

try:
    import ultra_light_processor  
    print('✅ ultra_light_processor.py - IMPORTA OK')
except Exception as e:
    print('❌ ultra_light_processor.py - ERROR:', e)

try:
    import robust_multi_engine_ocr
    print('✅ robust_multi_engine_ocr.py - IMPORTA OK') 
except Exception as e:
    print('❌ robust_multi_engine_ocr.py - ERROR:', e)
"

echo.
echo 3. Verificando memoria del contenedor...
docker stats ocr-backend --no-stream

echo.
echo 4. Copiando sistema de emergencia...
docker cp EMERGENCY_FIX.py ocr-backend:/app/

echo.
echo 5. Ejecutando sistema de emergencia (puerto 5001)...
echo   Esto debe responder en menos de 1 segundo
docker exec -d ocr-backend python /app/EMERGENCY_FIX.py

echo.
echo 6. Esperando 3 segundos...
timeout /t 3 /nobreak > nul

echo.
echo 7. Probando endpoint de emergencia...
curl -X GET http://localhost:8001/health
echo.
echo.

echo ========================================
echo   DIAGN■STICO COMPLETADO
echo ========================================
echo.
echo Si ves errores de importaci■n:
echo   - Los archivos no se copiaron correctamente
echo   - Hacer rebuild completo
echo.
echo Si el sistema de emergencia no responde:
echo   - Problema grave de memoria/configuraci■n
echo   - Usar docker-compose.optimized.yml
echo.
pause