#!/bin/bash
# Enhanced PyInstaller GUI - Linux Launcher Script
# This script runs the Enhanced PyInstaller GUI on Linux
# Make executable with: chmod +x run_gui.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Enhanced PyInstaller GUI - Linux Version${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 is not installed!"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora/RHEL:   sudo dnf install python3"
    echo "  Arch:          sudo pacman -S python"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python 3 is installed"

# Check if PyQt5 is installed
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} PyQt5 is not installed!"
    echo "Installing PyQt5..."
    pip3 install PyQt5
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to install PyQt5"
        echo "Try installing manually:"
        echo "  pip3 install PyQt5"
        echo "  or: pip3 install --user PyQt5"
        exit 1
    fi
fi

echo -e "${GREEN}[OK]${NC} PyQt5 is installed"

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} PyInstaller is not installed!"
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to install PyInstaller"
        echo "Try installing manually:"
        echo "  pip3 install pyinstaller"
        echo "  or: pip3 install --user pyinstaller"
        exit 1
    fi
fi

echo -e "${GREEN}[OK]${NC} PyInstaller is installed"
echo ""
echo -e "${GREEN}[INFO]${NC} Launching Enhanced PyInstaller GUI..."
echo ""

# Run the application
python3 enhanced_pyinstaller_gui.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[INFO]${NC} Application closed successfully"
else
    echo ""
    echo -e "${RED}[ERROR]${NC} Application encountered an error"
fi

