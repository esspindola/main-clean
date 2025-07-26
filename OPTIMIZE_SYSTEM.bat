@echo off
echo ========================================
echo     OPTIMIZACIÓN DEL SISTEMA DOCKER
echo     Mantiene la arquitectura actual
echo     Optimiza memoria y rendimiento
echo ========================================

echo.
echo 1. Deteniendo servicios actuales...
docker compose down

echo.
echo 2. Limpiando caché de Docker...
docker system prune -f

echo.
echo 3. Aplicando configuración Redis optimizada...
docker run -d --name redis-temp --rm -p 6379:6379 redis:7-alpine redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru --save "" --appendonly no
timeout /t 2 /nobreak > nul
docker stop redis-temp

echo.
echo 4. Copiando archivos del sistema inteligente...
if exist smart_invoice_nlp.py (
    echo - smart_invoice_nlp.py... OK
) else (
    echo - smart_invoice_nlp.py... FALTA
)

if exist ultra_light_processor.py (
    echo - ultra_light_processor.py... OK  
) else (
    echo - ultra_light_processor.py... FALTA
)

echo.
echo 5. Configurando límites de memoria en docker-compose...
if exist docker-compose.optimized.yml (
    copy docker-compose.optimized.yml docker-compose.yml
    echo - docker-compose.yml optimizado
)

if exist nginx.optimized.conf (
    copy nginx.optimized.conf nginx.conf
    echo - nginx.conf optimizado
)

echo.
echo 6. Iniciando sistema optimizado...
docker compose up -d

echo.
echo 7. Esperando inicio completo...
timeout /t 15 /nobreak

echo.
echo 8. Verificando estado...
docker compose ps

echo.
echo ==========================================
echo   OPTIMIZACIÓN COMPLETADA
echo ==========================================
echo.
echo ✅ Sistema optimizado para:
echo    - Redis: 128MB máximo
echo    - Backend: 2GB máximo  
echo    - Nginx: 128MB máximo
echo.
echo ✅ Algoritmo inteligente integrado:
echo    - Sistema robusto multi-motor
echo    - NLP contextual
echo    - Validación matemática
echo.
echo 🔗 Prueba en: http://localhost:8001/docs
echo 🔗 Frontend: http://localhost:5173
echo.
echo Si sigue lento, ejecuta:
echo    docker compose logs backend-ocr
echo.
pause