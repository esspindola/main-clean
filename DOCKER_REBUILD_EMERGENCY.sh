echo "🚨 EMERGENCY DOCKER REBUILD - FORZAR CAMBIOS 🚨"
echo "=================================================="

# 1. DETENER TODO
echo "🛑 Deteniendo todos los contenedores..."
docker-compose down --volumes --remove-orphans
docker stop $(docker ps -aq) 2>/dev/null || true

# 2. LIMPIAR CACHE AGRESIVAMENTE  
echo "🧹 Limpieza agresiva de cache..."
docker system prune -af --volumes
docker builder prune -af
docker image prune -af

# 3. REMOVER IMÁGENES ESPECÍFICAS
echo "🗑️ Removiendo imágenes del proyecto..."
docker rmi $(docker images "*ocr*" -q) 2>/dev/null || true
docker rmi $(docker images "*backend*" -q) 2>/dev/null || true

# 4. LIMPIAR VOLÚMENES
echo "💾 Limpiando volúmenes..."
docker volume prune -f

# 5. REBUILD SIN CACHE
echo "🏗️ Rebuild COMPLETO sin cache..."
docker-compose build --no-cache --pull

# 6. LEVANTAR SERVICIOS
echo "🚀 Iniciando servicios..."
docker-compose up -d

# 7. VERIFICAR
echo "✅ Verificando contenedores..."
docker-compose ps

echo ""
echo "🎯 VERIFICACIÓN:"
echo "- Espera 30 segundos para que el backend inicie"
echo "- Prueba en Swagger: http://localhost:8001/docs"
echo "- Busca el mensaje: 'EMERGENCY FIX 2025-07-24 22:15'"
echo ""
echo "📝 Si aún no funciona:"
echo "1. docker-compose logs backend-ocr"
echo "2. Verificar que el puerto 8001 esté libre"
echo "3. Reiniciar Docker Desktop completamente"