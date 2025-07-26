#!/bin/bash

# 🚀 Script de Instalación - ZatoBox
# Este script instala todas las dependencias del proyecto

echo "🎯 Iniciando instalación de ZatoBox..."

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

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    print_error "Node.js no está instalado. Por favor instala Node.js primero."
    exit 1
fi

print_success "Node.js encontrado: $(node --version)"

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado. Por favor instala npm primero."
    exit 1
fi

print_success "npm encontrado: $(npm --version)"

# Instalar dependencias del frontend
print_status "Instalando dependencias del frontend..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    print_success "Dependencias del frontend instaladas correctamente"
else
    print_error "Error al instalar dependencias del frontend"
    exit 1
fi
cd ..

# Instalar dependencias del backend
print_status "Instalando dependencias del backend..."
cd backend
npm install
if [ $? -eq 0 ]; then
    print_success "Dependencias del backend instaladas correctamente"
else
    print_error "Error al instalar dependencias del backend"
    exit 1
fi
cd ..

# Crear archivo .env si no existe
if [ ! -f "backend/.env" ]; then
    print_status "Creando archivo .env..."
    cp backend/env.example backend/.env
    print_success "Archivo .env creado"
else
    print_warning "Archivo .env ya existe"
fi

# Verificar que todo esté instalado correctamente
print_status "Verificando instalación..."

# Verificar frontend
cd frontend
if npm run build &> /dev/null; then
    print_success "Frontend compila correctamente"
else
    print_error "Error al compilar frontend"
    exit 1
fi
cd ..

# Verificar backend
cd backend
if node -c test-server.js &> /dev/null; then
    print_success "Backend sintácticamente correcto"
else
    print_error "Error de sintaxis en el backend"
    exit 1
fi
cd ..

print_success "🎉 Instalación completada exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura las variables de entorno en backend/.env"
echo "2. Ejecuta 'npm run dev' en la raíz para iniciar el frontend"
echo "3. Ejecuta 'node test-server.js' en backend/ para iniciar el servidor"
echo ""
echo "📚 Documentación disponible en docs/"
echo "🔧 Scripts disponibles en scripts/" 