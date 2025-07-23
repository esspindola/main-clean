#!/bin/bash

# 🏗️ Script de Build - ZatoBox
# Este script construye el proyecto para producción

echo "🏗️ Iniciando build de ZatoBox..."

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

# Verificar que estemos en el directorio correcto
if [ ! -f "package.json" ]; then
    print_error "No se encontró package.json. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Limpiar builds anteriores
print_status "Limpiando builds anteriores..."
if [ -d "frontend/dist" ]; then
    rm -rf frontend/dist
    print_success "Build anterior del frontend eliminado"
fi

# Build del frontend
print_status "Construyendo frontend..."
cd frontend
npm run build
if [ $? -eq 0 ]; then
    print_success "Frontend construido exitosamente"
else
    print_error "Error al construir frontend"
    exit 1
fi
cd ..

# Verificar que el build se creó correctamente
if [ -d "frontend/dist" ]; then
    print_success "Directorio dist creado correctamente"
    
    # Mostrar estadísticas del build
    FRONTEND_SIZE=$(du -sh frontend/dist | cut -f1)
    print_status "Tamaño del build del frontend: $FRONTEND_SIZE"
    
    # Contar archivos generados
    FILE_COUNT=$(find frontend/dist -type f | wc -l)
    print_status "Archivos generados: $FILE_COUNT"
else
    print_error "No se encontró el directorio dist"
    exit 1
fi

# Verificar sintaxis del backend
print_status "Verificando sintaxis del backend..."
cd backend
if node -c test-server.js; then
    print_success "Backend sintácticamente correcto"
else
    print_error "Error de sintaxis en el backend"
    exit 1
fi
cd ..

# Crear archivo de información del build
BUILD_INFO_FILE="build-info.txt"
echo "ZatoBox Build Information" > $BUILD_INFO_FILE
echo "=========================" >> $BUILD_INFO_FILE
echo "Fecha: $(date)" >> $BUILD_INFO_FILE
echo "Versión Node.js: $(node --version)" >> $BUILD_INFO_FILE
echo "Versión npm: $(npm --version)" >> $BUILD_INFO_FILE
echo "Tamaño frontend: $FRONTEND_SIZE" >> $BUILD_INFO_FILE
echo "Archivos generados: $FILE_COUNT" >> $BUILD_INFO_FILE
echo "Directorio dist: frontend/dist/" >> $BUILD_INFO_FILE

print_success "Información del build guardada en $BUILD_INFO_FILE"

print_success "🎉 Build completado exitosamente!"
echo ""
echo "📋 Información del build:"
echo "- Frontend: frontend/dist/"
echo "- Backend: backend/ (listo para producción)"
echo "- Información: $BUILD_INFO_FILE"
echo ""
echo "🚀 Para iniciar en producción:"
echo "1. Copia frontend/dist/ a tu servidor web"
echo "2. Ejecuta 'node test-server.js' en backend/"
echo "3. Configura las variables de entorno" 