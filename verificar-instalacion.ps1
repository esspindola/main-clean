# ==========================================
# ZatoBox v2.0 - Verificación de Instalación
# ==========================================
# Autor: ZatoBox Team
# Versión: 2.0.1
# Fecha: 2025-07-26
# ==========================================

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ZatoBox v2.0 - Verificacion de Instalacion" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Función para mostrar progreso
function Show-Progress($message, $color = "Yellow") {
    Write-Host "🔄 $message" -ForegroundColor $color
}

# Función para mostrar éxito
function Show-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

# Función para mostrar error
function Show-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

# Función para mostrar información
function Show-Info($message) {
    Write-Host "ℹ️ $message" -ForegroundColor Cyan
}

# Función para verificar si un comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# ==========================================
# VERIFICACIÓN DE DEPENDENCIAS
# ==========================================
Write-Host "🔍 Verificando dependencias del sistema..." -ForegroundColor Blue
Write-Host ""

# Verificar Node.js
if (Test-Command "node") {
    $nodeVersion = node --version
    Show-Success "Node.js: $nodeVersion"
} else {
    Show-Error "Node.js no encontrado"
}

# Verificar npm
if (Test-Command "npm") {
    $npmVersion = npm --version
    Show-Success "npm: $npmVersion"
} else {
    Show-Error "npm no encontrado"
}

# Verificar Python
$pythonCommand = $null
if (Test-Command "py") {
    $pythonVersion = py --version
    Show-Success "Python: $pythonVersion"
    $pythonCommand = "py"
} elseif (Test-Command "python") {
    $pythonVersion = python --version
    Show-Success "Python: $pythonVersion"
    $pythonCommand = "python"
} else {
    Show-Error "Python no encontrado"
}

# Verificar Tesseract OCR
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Show-Success "Tesseract OCR encontrado"
} else {
    Show-Error "Tesseract OCR no encontrado"
}

# Verificar Poppler
if (Test-Command "pdftoppm") {
    Show-Success "Poppler (PDF) encontrado"
} else {
    Show-Info "Poppler (PDF) no encontrado (opcional)"
}

# ==========================================
# VERIFICACIÓN DE ARCHIVOS DEL PROYECTO
# ==========================================
Write-Host ""
Write-Host "📁 Verificando archivos del proyecto..." -ForegroundColor Blue

$requiredFiles = @(
    "package.json",
    "frontend\package.json",
    "backend\package.json",
    "backend\test-server.js",
    "app-light-fixed.py",
    "requirements-light.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Show-Success "$file"
    } else {
        Show-Error "$file"
    }
}

# ==========================================
# VERIFICACIÓN DE DEPENDENCIAS INSTALADAS
# ==========================================
Write-Host ""
Write-Host "📦 Verificando dependencias instaladas..." -ForegroundColor Blue

# Verificar node_modules del proyecto principal
if (Test-Path "node_modules") {
    Show-Success "node_modules (proyecto principal)"
} else {
    Show-Error "node_modules (proyecto principal)"
}

# Verificar node_modules del frontend
if (Test-Path "frontend\node_modules") {
    Show-Success "node_modules (frontend)"
} else {
    Show-Error "node_modules (frontend)"
}

# Verificar node_modules del backend
if (Test-Path "backend\node_modules") {
    Show-Success "node_modules (backend)"
} else {
    Show-Error "node_modules (backend)"
}

# ==========================================
# VERIFICACIÓN DE PUERTOS
# ==========================================
Write-Host ""
Write-Host "🔌 Verificando puertos..." -ForegroundColor Blue

$ports = @(
    @{Port = 4444; Service = "Backend"},
    @{Port = 5173; Service = "Frontend"},
    @{Port = 5000; Service = "OCR"}
)

foreach ($portInfo in $ports) {
    $port = $portInfo.Port
    $service = $portInfo.Service
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Show-Error "$service (puerto $port) - OCUPADO"
        } else {
            Show-Success "$service (puerto $port) - LIBRE"
        }
    } catch {
        Show-Success "$service (puerto $port) - LIBRE"
    }
}

# ==========================================
# VERIFICACIÓN DE DIRECTORIOS
# ==========================================
Write-Host ""
Write-Host "📂 Verificando directorios..." -ForegroundColor Blue

$directories = @(
    "uploads",
    "uploads\products",
    "uploads\ocr",
    "outputs"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Show-Success "Directorio $dir"
    } else {
        Show-Error "Directorio $dir"
    }
}

# ==========================================
# VERIFICACIÓN DE SCRIPTS
# ==========================================
Write-Host ""
Write-Host "📜 Verificando scripts..." -ForegroundColor Blue

$scripts = @(
    "install-zatobox.ps1",
    "start-zatobox.ps1",
    "verificar-instalacion.ps1"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Show-Success "Script $script"
    } else {
        Show-Error "Script $script"
    }
}

# ==========================================
# VERIFICACIÓN DE CONFIGURACIÓN OCR
# ==========================================
Write-Host ""
Write-Host "🔍 Verificando configuración OCR..." -ForegroundColor Blue

# Verificar configuración de Tesseract en app-light-fixed.py
if (Test-Path "app-light-fixed.py") {
    $content = Get-Content "app-light-fixed.py" -Raw
    if ($content -match "pytesseract\.pytesseract\.tesseract_cmd") {
        Show-Success "Configuración Tesseract en app-light-fixed.py"
    } else {
        Show-Error "Configuración Tesseract faltante en app-light-fixed.py"
    }
} else {
    Show-Error "app-light-fixed.py no encontrado"
}

# ==========================================
# VERIFICACIÓN DE CONFIGURACIÓN FRONTEND
# ==========================================
Write-Host ""
Write-Host "🎨 Verificando configuración Frontend..." -ForegroundColor Blue

# Verificar configuración de API en frontend
if (Test-Path "frontend\src\config\api.ts") {
    $content = Get-Content "frontend\src\config\api.ts" -Raw
    if ($content -match "http://127\.0\.0\.1:5000") {
        Show-Success "Configuración OCR correcta en frontend (puerto 5000)"
    } else {
        Show-Error "Configuración OCR incorrecta en frontend (debe ser puerto 5000)"
    }
} else {
    Show-Error "frontend\src\config\api.ts no encontrado"
}

# ==========================================
# RESULTADO FINAL
# ==========================================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  RESUMEN DE VERIFICACIÓN" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Contar errores
$errorCount = 0
$successCount = 0

# Contar errores en la salida anterior
$output = Get-Content $PSCommandPath | Select-String "Show-Error|Show-Success"
foreach ($line in $output) {
    if ($line -match "Show-Error") {
        $errorCount++
    } elseif ($line -match "Show-Success") {
        $successCount++
    }
}

if ($errorCount -eq 0) {
    Write-Host "🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ ZatoBox v2.0 está listo para usar" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Para iniciar el sistema:" -ForegroundColor Yellow
    Write-Host "   .\start-zatobox.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 URLs de acceso:" -ForegroundColor Yellow
    Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "   Backend:  http://localhost:4444" -ForegroundColor Cyan
    Write-Host "   OCR:      http://localhost:5000" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ SE ENCONTRARON $errorCount PROBLEMAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Soluciones recomendadas:" -ForegroundColor Yellow
    Write-Host "   1. Ejecuta .\install-zatobox.ps1 para reinstalar" -ForegroundColor White
    Write-Host "   2. Verifica que todas las dependencias estén instaladas" -ForegroundColor White
    Write-Host "   3. Asegúrate de que los puertos estén libres" -ForegroundColor White
    Write-Host "   4. Revisa la documentación en README.md" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 Para más información, consulta el README.md" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Green 