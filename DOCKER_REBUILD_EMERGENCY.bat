@echo off
echo 🚨 EMERGENCY DOCKER REBUILD - FORZAR CAMBIOS 🚨
echo ==================================================

echo 🛑 Deteniendo todos los contenedores...
docker-compose down --volumes --remove-orphans
docker stop $(docker ps -aq) 2>nul

echo 🧹 Limpieza agresiva de cache...
docker system prune -af --volumes
docker builder prune -af
docker image prune -af

echo 🗑️ Removiendo imágenes del proyecto...
for /f %%i in ('docker images "*ocr*" -q 2^>nul') do docker rmi %%i 2>nul
for /f %%i in ('docker images "*backend*" -q 2^>nul') do docker rmi %%i 2>nul

echo 💾 Limpiando volúmenes...
docker volume prune -f

echo 🏗️ Rebuild COMPLETO sin cache...
docker-compose build --no-cache --pull

echo 🚀 Iniciando servicios...
docker-compose up -d

echo ✅ Verificando contenedores...
docker-compose ps

echo.
echo 🎯 VERIFICACIÓN:
echo - Espera 30 segundos para que el backend inicie
echo - Prueba en Swagger: http://localhost:8001/docs
echo - Busca el mensaje: 'EMERGENCY FIX 2025-07-24 22:15'
echo.
echo 📝 Si aún no funciona:
echo 1. docker-compose logs backend-ocr
echo 2. Verificar que el puerto 8001 esté libre
echo 3. Reiniciar Docker Desktop completamente
pause