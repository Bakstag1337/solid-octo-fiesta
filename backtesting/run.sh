#!/bin/bash
# Startup script for Backtesting Platform

echo "🚀 Starting Backtesting Platform..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Dependencies not found. Installing..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🌐 Starting Streamlit app..."
echo "📊 Open your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run frontend/app.py
