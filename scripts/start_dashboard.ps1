# Streamlit Dashboard Startup Script (Windows PowerShell)

# Display header
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📧 Email Classification Dashboard" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
    & ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment created and activated" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing/Updating dependencies..." -ForegroundColor Yellow

# Install required packages
pip install -q streamlit==1.28.1 plotly==5.18.0 pandas==2.1.3 motor==3.3.2 python-dotenv==1.0.0 > $null 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Error installing dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Dashboard..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
$mongoUrl = $env:MONGODB_URL -or "mongodb://admin:changeme123@mongodb:27017"
$mongoDb = $env:MONGODB_DB_NAME -or "email_classifier"
Write-Host "  - MongoDB URL: $mongoUrl" -ForegroundColor Gray
Write-Host "  - Database: $mongoDb" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
streamlit run streamlit_dashboard.py

# Handle exit
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Dashboard stopped with error code: $LASTEXITCODE" -ForegroundColor Red
    pause
}
