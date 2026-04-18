#!/bin/bash
# Streamlit Dashboard Startup Script (Linux/Mac)

echo "=========================================="
echo "📧 Email Classification Dashboard"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✓ Virtual environment found"
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

echo ""
echo "Installing/Updating dependencies..."
pip install -q streamlit==1.28.1 plotly==5.18.0 pandas==2.1.3 motor==3.3.2 python-dotenv==1.0.0

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

echo ""
echo "=========================================="
echo "🚀 Starting Dashboard..."
echo "=========================================="
echo ""
echo "Dashboard will open at: http://localhost:8501"
echo ""
echo "Configuration:"
echo "  - MongoDB URL: ${MONGODB_URL:-mongodb://admin:changeme123@mongodb:27017}"
echo "  - Database: ${MONGODB_DB_NAME:-email_classifier}"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Run Streamlit
streamlit run streamlit_dashboard.py
