# 🚀 ZatoBox v2.0 - Script de Inicio Automático
# Este script inicia todos los servicios de ZatoBox automáticamente

param(
    [switch]$Silent = $false
)

# Configuración de colores
$Green = "Green"
$Blue = "Blue"
$Yellow = "Yellow"
$Red = "Red"
$White = "White"

# Función para mostrar mensajes
function Write-Status {
    param(
        [string]$Message,
        [string]$Color = $White,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Type) {
        "SUCCESS" { "[OK]" }
        "ERROR" { "[ERROR]" }
        "WARNING" { "[WARN]" }
        "INFO" { "[INFO]" }
        default { "[INFO]" }
    }
    
    Write-Host "[$timestamp] $prefix $Message" -ForegroundColor $Color
}

# Función para verificar si un puerto está en uso
function Test-Port {
    param([int]$Port)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $connection -ne $null
    }
    catch {
        return $false
    }
}

# Función para detener procesos en un puerto
function Stop-ProcessOnPort {
    param([int]$Port)
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                    Select-Object -ExpandProperty OwningProcess | 
                    ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }
        
        foreach ($process in $processes) {
            Write-Status "Deteniendo proceso $($process.ProcessName) (PID: $($process.Id)) en puerto $Port" $Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        
        Start-Sleep -Seconds 2
        return $true
    }
    catch {
        Write-Status "Error al detener procesos en puerto $Port" $Red "ERROR"
        return $false
    }
}

# Función para configurar PATH de Tesseract
function Set-TesseractPath {
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    
    if (Test-Path $tesseractPath) {
        $env:PATH += ";$tesseractPath"
        Write-Status "Tesseract PATH configurado: $tesseractPath" $Green "SUCCESS"
        return $true
    }
    else {
        Write-Status "Tesseract no encontrado en $tesseractPath" $Red "ERROR"
        Write-Status "Por favor instale Tesseract OCR primero" $Yellow "WARNING"
        return $false
    }
}

# Función para crear directorios necesarios
function Create-RequiredDirectories {
    $directories = @(
        "uploads",
        "uploads\products",
        "uploads\ocr",
        "outputs"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Directorio creado: $dir" $Green "SUCCESS"
        }
    }
}

# Función para verificar comandos
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Función para obtener el comando de Python correcto
function Get-PythonCommand {
    if (Test-Command "py") {
        return "py"
    } elseif (Test-Command "python") {
        return "python"
    } else {
        return $null
    }
}

# Función para mostrar información de acceso
function Show-AccessInfo {
    Write-Host ""
    Write-Host "ZatoBox v2.0 iniciado exitosamente!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "URLs de acceso:" -ForegroundColor $Yellow
    Write-Host "   Frontend: http://localhost:5173" -ForegroundColor $White
    Write-Host "   Backend:  http://localhost:4444" -ForegroundColor $White
    Write-Host "   OCR:      http://localhost:5000" -ForegroundColor $White
    Write-Host ""
    Write-Host "Credenciales de prueba:" -ForegroundColor $Yellow
    Write-Host "   Email: admin@frontposw.com" -ForegroundColor $White
    Write-Host "   Password: admin12345678" -ForegroundColor $White
    Write-Host ""
    Write-Host "Para más información, consulta el README.md" -ForegroundColor $Blue
    Write-Host ""
}

# ==========================================
# INICIO DEL SCRIPT
# ==========================================
Write-Host "==========================================" -ForegroundColor $Green
Write-Host "  ZatoBox v2.0 - Inicio Automático" -ForegroundColor $Green
Write-Host "==========================================" -ForegroundColor $Green
Write-Host ""

# Verificar requisitos
Write-Status "Verificando requisitos del sistema..." $Blue

# Verificar Node.js
if (-not (Test-Command "node")) {
    Write-Status "Node.js no encontrado. Por favor instale Node.js primero." $Red "ERROR"
    exit 1
}
$nodeVersion = node --version
Write-Status "Node.js detectado: $nodeVersion" $Green "SUCCESS"

# Verificar npm
if (-not (Test-Command "npm")) {
    Write-Status "npm no encontrado. Por favor instale Node.js primero." $Red "ERROR"
    exit 1
}
$npmVersion = npm --version
Write-Status "npm detectado: $npmVersion" $Green "SUCCESS"

# Verificar Python
$pythonCommand = Get-PythonCommand
if (-not $pythonCommand) {
    Write-Status "Python no encontrado. Por favor instale Python 3.12 primero." $Red "ERROR"
    exit 1
}
$pythonVersion = & $pythonCommand --version
Write-Status "Python detectado: $pythonVersion" $Green "SUCCESS"

# Configurar Tesseract
if (-not (Set-TesseractPath)) {
    Write-Status "Tesseract no configurado correctamente" $Red "ERROR"
    exit 1
}

# Crear directorios necesarios
Create-RequiredDirectories

# ==========================================
# DETENER SERVICIOS EXISTENTES
# ==========================================
Write-Status "Deteniendo servicios existentes..." $Yellow

$ports = @(4444, 5173, 5000)
foreach ($port in $ports) {
    if (Test-Port $port) {
        Stop-ProcessOnPort $port
    }
}

Start-Sleep -Seconds 3

# ==========================================
# INICIAR SERVICIOS
# ==========================================
Write-Status "Iniciando servicios de ZatoBox..." $Blue

# Iniciar Backend
Write-Status "Iniciando Backend (puerto 4444)..." $Yellow
try {
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\backend
        node test-server.js
    }
    Write-Status "Backend iniciado correctamente" $Green "SUCCESS"
} catch {
    Write-Status "Error al iniciar Backend: $($_.Exception.Message)" $Red "ERROR"
    exit 1
}

# Esperar a que el backend esté listo
Start-Sleep -Seconds 5

# Iniciar Frontend
Write-Status "Iniciando Frontend (puerto 5173)..." $Yellow
try {
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\frontend
        npm run dev
    }
    Write-Status "Frontend iniciado correctamente" $Green "SUCCESS"
} catch {
    Write-Status "Error al iniciar Frontend: $($_.Exception.Message)" $Red "ERROR"
    exit 1
}

# Esperar a que el frontend esté listo
Start-Sleep -Seconds 5

# Iniciar Servidor OCR
Write-Status "Iniciando Servidor OCR (puerto 5000)..." $Yellow
try {
    $ocrJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        $venvPython = Join-Path $using:PWD ".venv\Scripts\python.exe"
        $env:PATH += ";C:\Program Files\Tesseract-OCR"
        $logFile = Join-Path $using:PWD "ocr_output.log"
        $errorFile = Join-Path $using:PWD "ocr_error.log"
        try {
            & $venvPython app-light-fixed.py *> $logFile 2> $errorFile
        } catch {
            $errorMessage = $_.Exception.Message
            "Error: $errorMessage" | Out-File -FilePath $errorFile -Append -Encoding UTF8
            throw $_
        }
    }
    Write-Status "Servidor OCR iniciado correctamente" $Green "SUCCESS"
} catch {
    Write-Status "Error al iniciar Servidor OCR: $($_.Exception.Message)" $Red "ERROR"
    Write-Status "Revisa los archivos ocr_output.log y ocr_error.log para más detalles." $Yellow "WARNING"
    exit 1
}

# Esperar a que el OCR esté listo
Start-Sleep -Seconds 5

# ==========================================
# VERIFICAR SERVICIOS
# ==========================================
Write-Status "Verificando servicios..." $Blue

$servicesStatus = @{
    "Backend (4444)" = $false
    "Frontend (5173)" = $false
    "OCR (5000)" = $false
}

# Verificar Backend
if (Test-Port 4444) {
    $servicesStatus["Backend (4444)"] = $true
    Write-Status "Backend: OK" $Green "SUCCESS"
} else {
    Write-Status "Backend: ERROR" $Red "ERROR"
}

# Verificar Frontend
if (Test-Port 5173) {
    $servicesStatus["Frontend (5173)"] = $true
    Write-Status "Frontend: OK" $Green "SUCCESS"
} else {
    Write-Status "Frontend: ERROR" $Red "ERROR"
}

# Verificar OCR
if (Test-Port 5000) {
    $servicesStatus["OCR (5000)"] = $true
    Write-Status "OCR: OK" $Green "SUCCESS"
} else {
    Write-Status "OCR: ERROR" $Red "ERROR"
}

# ==========================================
# RESULTADO FINAL
# ==========================================
$allServicesRunning = $servicesStatus.Values -notcontains $false

if ($allServicesRunning) {
    Show-AccessInfo
} else {
    Write-Host ""
    Write-Host "Algunos servicios no se iniciaron correctamente" -ForegroundColor $Red
    Write-Host ""
    foreach ($service in $servicesStatus.Keys) {
        $status = if ($servicesStatus[$service]) { "[OK]" } else { "[ERROR]" }
        $color = if ($servicesStatus[$service]) { $Green } else { $Red }
        Write-Host "   $service : $status" -ForegroundColor $color
    }
    Write-Host ""
    Write-Host "Solución de problemas:" -ForegroundColor $Yellow
    Write-Host "   1. Verifica que los puertos 4444, 5173 y 5000 estén libres" -ForegroundColor $White
    Write-Host "   2. Asegúrate de que todas las dependencias estén instaladas" -ForegroundColor $White
    Write-Host "   3. Ejecuta .\install-zatobox.ps1 para reinstalar" -ForegroundColor $White
    Write-Host ""
}

# ==========================================
# MONITOREO CONTINUO (OPCIONAL)
# ==========================================
if (-not $Silent) {
    Write-Host ""
    Write-Host "Monitoreo de servicios activo..." -ForegroundColor $Blue
    Write-Host "Presiona Ctrl+C para detener todos los servicios" -ForegroundColor $Yellow
    Write-Host ""
    
    try {
        while ($true) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            $backendStatus = if (Test-Port 4444) { "[OK]" } else { "[ERROR]" }
            $frontendStatus = if (Test-Port 5173) { "[OK]" } else { "[ERROR]" }
            $ocrStatus = if (Test-Port 5000) { "[OK]" } else { "[ERROR]" }
            
            Write-Host "[$timestamp] Backend: $backendStatus | Frontend: $frontendStatus | OCR: $ocrStatus" -ForegroundColor $White
            
            Start-Sleep -Seconds 30
        }
    }
    catch {
        Write-Host ""
        Write-Status "Deteniendo servicios..." $Yellow
        
        # Detener jobs
        if ($backendJob) { Stop-Job $backendJob; Remove-Job $backendJob }
        if ($frontendJob) { Stop-Job $frontendJob; Remove-Job $frontendJob }
        if ($ocrJob) { Stop-Job $ocrJob; Remove-Job $ocrJob }
        
        Write-Status "Servicios detenidos" $Green "SUCCESS"
    }
}