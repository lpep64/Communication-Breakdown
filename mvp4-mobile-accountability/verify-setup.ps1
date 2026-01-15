# Guardian Protocol - Setup Verification Script
# Run this to verify your environment is ready

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Guardian Protocol - Setup Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    Write-Host "  ✓ npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ npm not found. Install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check directory structure
Write-Host "Checking project structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\main.py",
    "backend\crypto_utils.py",
    "backend\requirements.txt",
    "frontend\src\App.js",
    "frontend\src\index.js",
    "frontend\package.json",
    "README.md"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "Some files are missing. Please check the project structure." -ForegroundColor Red
    exit 1
}

# Check virtual environment
Write-Host "Checking Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "guardian-env\Scripts\Activate.ps1") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment not found" -ForegroundColor Yellow
    Write-Host "    Run: python -m venv guardian-env" -ForegroundColor Cyan
}

# Check backend dependencies
Write-Host "Checking backend dependencies..." -ForegroundColor Yellow
if (Test-Path "guardian-env\Lib\site-packages\fastapi") {
    Write-Host "  ✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Backend dependencies not installed" -ForegroundColor Yellow
    Write-Host "    Run: .\guardian-env\Scripts\Activate.ps1; cd backend; pip install -r requirements.txt" -ForegroundColor Cyan
}

# Check frontend dependencies
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Frontend dependencies not installed" -ForegroundColor Yellow
    Write-Host "    Run: cd frontend; npm install" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup verification complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create virtual environment (if needed):" -ForegroundColor White
Write-Host "   python -m venv guardian-env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Install backend dependencies:" -ForegroundColor White
Write-Host "   .\guardian-env\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Install frontend dependencies:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm install" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Start backend (in one terminal):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   uvicorn main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Start frontend (in another terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "See QUICKSTART.md for detailed instructions!" -ForegroundColor Green
