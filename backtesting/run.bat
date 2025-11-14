@echo off
REM Startup script for Backtesting Platform (Windows)

echo 🚀 Starting Backtesting Platform...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencies not found. Installing...
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies already installed
)

echo.
echo 🌐 Starting Streamlit app...
echo 📊 Open your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

REM Run Streamlit
streamlit run frontend/app.py

pause
