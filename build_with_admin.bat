@echo off
REM Build script for Enhanced PyInstaller GUI with Administrator Privileges
REM This script requires Administrator rights to run

echo ========================================
echo Enhanced PyInstaller GUI - Build Script
echo ========================================
echo.
echo This will build the Enhanced PyInstaller GUI with Administrator privileges.
echo The resulting executable will always request admin rights when launched.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
) else (
    echo [ERROR] This script must be run as Administrator!
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] PyInstaller is not installed!
    echo Please install it with: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo [INFO] Building Enhanced PyInstaller GUI...
echo.

REM Build with PyInstaller using the manifest for admin privileges
pyinstaller --onefile ^
    --windowed ^
    --name "Enhanced_PyInstaller_GUI" ^
    --icon=app_icon.ico ^
    --uac-admin ^
    --manifest=admin_manifest.xml ^
    --add-data "modern_stylesheet.py;." ^
    --add-data "drag_drop_support.py;." ^
    --add-data "async_file_system.py;." ^
    --add-data "batch_conversion.py;." ^
    --add-data "config_profiles.py;." ^
    --add-data "update_manager.py;." ^
    --add-data "version.json;." ^
    --clean ^
    enhanced_pyinstaller_gui.py

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Build completed successfully!
    echo ========================================
    echo.
    echo The executable is located in: dist\Enhanced_PyInstaller_GUI.exe
    echo.
    echo This executable will request Administrator privileges when launched.
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause

