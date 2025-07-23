#!/bin/bash

# 🚀 Script de Despliegue - ZatoBox
# Este script despliega el proyecto en producción

echo "🚀 Iniciando despliegue de ZatoBox..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    print_error "Uso: $0 <ambiente> [opciones]"
    echo ""
    echo "Ambientes disponibles:"
    echo "  development  - Despliegue en desarrollo"
    echo "  staging      - Despliegue en staging"
    echo "  production   - Despliegue en producción"
    echo ""
    echo "Opciones:"
    echo "  --build      - Construir antes del despliegue"
    echo "  --backup     - Crear backup antes del despliegue"
    echo "  --restart    - Reiniciar servicios después del despliegue"
    exit 1
fi

ENVIRONMENT=$1
BUILD_FLAG=false
BACKUP_FLAG=false
RESTART_FLAG=false

# Procesar opciones
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG=true
            shift
            ;;
        --backup)
            BACKUP_FLAG=true
            shift
            ;;
        --restart)
            RESTART_FLAG=true
            shift
            ;;
        *)
            print_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

print_status "Ambiente: $ENVIRONMENT"
print_status "Build: $BUILD_FLAG"
print_status "Backup: $BACKUP_FLAG"
print_status "Restart: $RESTART_FLAG"

# Verificar que estemos en el directorio correcto
if [ ! -f "package.json" ]; then
    print_error "No se encontró package.json. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Crear backup si se solicita
if [ "$BACKUP_FLAG" = true ]; then
    print_status "Creando backup..."
    BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup del frontend
    if [ -d "frontend/dist" ]; then
        cp -r frontend/dist $BACKUP_DIR/
        print_success "Backup del frontend creado"
    fi
    
    # Backup del backend
    cp -r backend $BACKUP_DIR/
    print_success "Backup del backend creado"
    
    print_success "Backup completo guardado en $BACKUP_DIR/"
fi

# Construir si se solicita
if [ "$BUILD_FLAG" = true ]; then
    print_status "Construyendo proyecto..."
    ./scripts/build.sh
    if [ $? -ne 0 ]; then
        print_error "Error en el build. Abortando despliegue."
        exit 1
    fi
fi

# Verificar que el build existe
if [ ! -d "frontend/dist" ]; then
    print_error "No se encontró el build del frontend. Ejecuta --build primero."
    exit 1
fi

# Configuraciones específicas por ambiente
case $ENVIRONMENT in
    development)
        print_status "Configurando para desarrollo..."
        DEPLOY_DIR="./deploy-dev"
        PORT=4444
        NODE_ENV="development"
        ;;
    staging)
        print_status "Configurando para staging..."
        DEPLOY_DIR="./deploy-staging"
        PORT=4444
        NODE_ENV="staging"
        ;;
    production)
        print_status "Configurando para producción..."
        DEPLOY_DIR="./deploy-prod"
        PORT=4444
        NODE_ENV="production"
        ;;
    *)
        print_error "Ambiente no válido: $ENVIRONMENT"
        exit 1
        ;;
esac

# Crear directorio de despliegue
print_status "Creando directorio de despliegue: $DEPLOY_DIR"
mkdir -p $DEPLOY_DIR

# Copiar frontend
print_status "Copiando frontend..."
cp -r frontend/dist/* $DEPLOY_DIR/
print_success "Frontend copiado"

# Copiar backend
print_status "Copiando backend..."
cp -r backend $DEPLOY_DIR/
print_success "Backend copiado"

# Crear archivo de configuración del despliegue
DEPLOY_CONFIG="$DEPLOY_DIR/deploy-config.json"
cat > $DEPLOY_CONFIG << EOF
{
  "environment": "$ENVIRONMENT",
  "deployDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)",
  "port": $PORT,
  "nodeEnv": "$NODE_ENV"
}
EOF

print_success "Configuración de despliegue creada"

# Crear script de inicio
START_SCRIPT="$DEPLOY_DIR/start.sh"
cat > $START_SCRIPT << 'EOF'
#!/bin/bash
cd backend
NODE_ENV=production node test-server.js
EOF

chmod +x $START_SCRIPT
print_success "Script de inicio creado"

# Crear archivo .env para producción si no existe
if [ ! -f "$DEPLOY_DIR/backend/.env" ]; then
    print_status "Creando archivo .env para producción..."
    cp backend/env.example $DEPLOY_DIR/backend/.env
    print_warning "Recuerda configurar las variables de entorno en $DEPLOY_DIR/backend/.env"
fi

# Reiniciar servicios si se solicita
if [ "$RESTART_FLAG" = true ]; then
    print_status "Reiniciando servicios..."
    
    # Detener procesos existentes
    pkill -f "node test-server.js" 2>/dev/null || true
    print_success "Procesos anteriores detenidos"
    
    # Iniciar nuevo proceso
    cd $DEPLOY_DIR
    nohup ./start.sh > server.log 2>&1 &
    DEPLOY_PID=$!
    print_success "Servidor iniciado con PID: $DEPLOY_PID"
    
    # Verificar que el servidor esté funcionando
    sleep 3
    if curl -s http://localhost:$PORT/health > /dev/null; then
        print_success "Servidor respondiendo correctamente"
    else
        print_warning "Servidor no responde inmediatamente. Revisa server.log"
    fi
fi

# Mostrar información del despliegue
print_success "🎉 Despliegue completado exitosamente!"
echo ""
echo "📋 Información del despliegue:"
echo "- Ambiente: $ENVIRONMENT"
echo "- Directorio: $DEPLOY_DIR"
echo "- Puerto: $PORT"
echo "- Configuración: $DEPLOY_CONFIG"
echo "- Script de inicio: $START_SCRIPT"
echo ""
echo "🚀 Para iniciar el servidor:"
echo "cd $DEPLOY_DIR && ./start.sh"
echo ""
echo "📊 Para monitorear:"
echo "tail -f $DEPLOY_DIR/server.log" 