param(
    [int]$Port = 8000,
    [switch]$SkipFrontendBuild,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Command($Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Yellow
Write-Host " ToolHub local runner" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (!(Test-Path $PythonExe)) {
    Write-Step "Creating Python virtual environment"
    if (!(Test-Command "python")) {
        throw "python was not found. Please install Python 3.12+ first."
    }
    python -m venv .venv
}

if (!$SkipInstall) {
    Write-Step "Installing backend dependencies"
    & $PythonExe -m pip install --upgrade pip
    & $PythonExe -m pip install -r requirements.txt
}

if (!(Test-Path (Join-Path $ProjectRoot ".env"))) {
    Write-Step "Creating local .env"
    $LocalSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object { [char]$_ })
    $LocalPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
    @"
DJANGO_SECRET_KEY=$LocalSecret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:$Port,http://localhost:$Port
DJANGO_CORS_ORIGINS=http://127.0.0.1:$Port,http://localhost:$Port
DATABASE_URL=
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=$LocalPassword
DJANGO_SUPERUSER_EMAIL=admin@example.com
"@ | Set-Content -Path ".env" -Encoding UTF8
    Write-Host "Local admin password written to .env: $LocalPassword" -ForegroundColor Yellow
}
else {
    $EnvText = Get-Content ".env" -Raw
    if ($EnvText -notmatch "DJANGO_ALLOWED_HOSTS=.*127\.0\.0\.1") {
        Write-Step "Patching .env for local hosts"
        $EnvText = $EnvText -replace "DJANGO_DEBUG=.*", "DJANGO_DEBUG=True"
        $EnvText = $EnvText -replace "DJANGO_ALLOWED_HOSTS=.*", "DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost"
        $EnvText = $EnvText -replace "DJANGO_CSRF_TRUSTED_ORIGINS=.*", "DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:$Port,http://localhost:$Port"
        $EnvText = $EnvText -replace "DJANGO_CORS_ORIGINS=.*", "DJANGO_CORS_ORIGINS=http://127.0.0.1:$Port,http://localhost:$Port"
        Set-Content -Path ".env" -Value $EnvText -Encoding UTF8
    }
}

Write-Step "Running database migrations"
& $PythonExe manage.py migrate

if (!$SkipFrontendBuild) {
    Write-Step "Building Vue frontend"
    Push-Location "frontend"
    try {
        if (!(Test-Command "npm")) {
            throw "npm was not found. Please install Node.js first."
        }
        if (!(Test-Path "node_modules") -and !$SkipInstall) {
            npm install
        }
        npm run build
    }
    finally {
        Pop-Location
    }
}

Write-Step "Checking port"
$PortInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($PortInUse) {
    throw "Port $Port is already in use. Try: .\run-local.ps1 -Port 8001"
}

Write-Host ""
Write-Host "Open the site:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:$Port/" -ForegroundColor Green
Write-Host "Open Django admin:" -ForegroundColor Green
Write-Host "  http://127.0.0.1:$Port/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

& $PythonExe manage.py runserver "127.0.0.1:$Port"
