#!/usr/bin/env python3
"""
Test script for Enhanced PyInstaller GUI - Linux Version
This script verifies that all dependencies are installed and the application can run.
"""

import sys
import platform

print("=" * 70)
print("Enhanced PyInstaller GUI - Linux Version Test")
print("=" * 70)
print()

# Check Python version
print(f"✓ Python version: {platform.python_version()}")
print(f"✓ Platform: {platform.system()} {platform.release()}")
print(f"✓ Architecture: {platform.machine()}")
print()

# Check for required modules
errors = []
warnings = []

print("Checking dependencies...")
print("-" * 70)

# Required modules
required_modules = [
    ('PyQt5', 'PyQt5'),
    ('PyQt5.QtWidgets', 'PyQt5 QtWidgets'),
    ('PyQt5.QtCore', 'PyQt5 QtCore'),
    ('PyQt5.QtGui', 'PyQt5 QtGui'),
    ('PyInstaller', 'PyInstaller'),
]

for module_name, display_name in required_modules:
    try:
        __import__(module_name)
        print(f"  ✓ {display_name}")
    except ImportError as e:
        print(f"  ✗ {display_name} - NOT FOUND")
        errors.append(f"{display_name}: {str(e)}")

print()

# Check application files
print("Checking application files...")
print("-" * 70)

import os

required_files = [
    'enhanced_pyinstaller_gui.py',
    'config_profiles.py',
    'modern_stylesheet.py',
    'drag_drop_support.py',
    'batch_conversion.py',
    'async_file_system.py',
    'update_manager.py',
    'version.json',
]

for filename in required_files:
    if os.path.exists(filename):
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ {filename} - NOT FOUND")
        errors.append(f"Missing file: {filename}")

print()

# Platform-specific checks
if platform.system() == 'Linux':
    print("✓ Running on Linux - This is the correct version!")
elif platform.system() == 'Darwin':
    print("⚠ Running on macOS - Should work but not fully tested")
    warnings.append("Running on macOS (not fully tested)")
elif platform.system() == 'Windows':
    print("⚠ WARNING: Running on Windows!")
    print("  This is the Linux version. For Windows, use the parent directory version.")
    warnings.append("Wrong platform - use Windows version instead")

print()

# Summary
print("=" * 70)
if errors:
    print("✗ TEST FAILED")
    print()
    print("Errors found:")
    for error in errors:
        print(f"  - {error}")
    print()
    print("To install missing dependencies:")
    print("  pip3 install PyQt5 pyinstaller")
    sys.exit(1)
elif warnings:
    print("⚠ TEST PASSED WITH WARNINGS")
    print()
    print("Warnings:")
    for warning in warnings:
        print(f"  - {warning}")
    print()
else:
    print("✓ ALL TESTS PASSED!")
    print()
    print("You can now run the application:")
    print("  ./run_gui.sh")
    print("  or")
    print("  python3 enhanced_pyinstaller_gui.py")

print("=" * 70)
print()


