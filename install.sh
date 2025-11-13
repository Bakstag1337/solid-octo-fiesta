#!/bin/bash

echo "==================================="
echo "  Desktop System Monitor Installer"
echo "==================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✓ pip3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --user

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Make the script executable
chmod +x src/sysmon.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run the system monitor:"
echo "  ./src/sysmon.py"
echo ""
echo "Or:"
echo "  python3 src/sysmon.py"
echo ""
echo "Enjoy! 🚀"
