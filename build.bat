@echo off
REM Build script for Enhanced PyInstaller GUI
REM No administrator privileges required for building

echo ========================================
echo Enhanced PyInstaller GUI - Build Script
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

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
echo [INFO] Working directory: %CD%
echo.

REM Build with PyInstaller (--uac-admin makes OUTPUT exe request admin, not build process)
pyinstaller --onefile ^
    --windowed ^
    --name "Enhanced_PyInstaller_GUI" ^
    --icon=app_icon.ico ^
    --uac-admin ^
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
    echo NOTE: The executable will request Administrator privileges when launched.
    echo This is due to the --uac-admin flag (required for PyInstaller to work properly).
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
