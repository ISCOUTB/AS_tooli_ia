# Script para ejecutar el backend Tooli-IA
Write-Host "🚀 Iniciando Tooli-IA Backend..." -ForegroundColor Green

# Activar entorno virtual
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Verificar que el entorno está activado
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Entorno virtual activado: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "❌ Error: No se pudo activar el entorno virtual" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Cambiar al directorio del backend
Set-Location "agent"

# Ejecutar el servidor
Write-Host "🔥 Ejecutando servidor Flask..." -ForegroundColor Cyan
python tooli-core.py

# Mantener la ventana abierta si hay error
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ El servidor se detuvo con errores" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
}