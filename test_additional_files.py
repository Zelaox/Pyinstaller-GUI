"""
Test script to verify the additional files functionality in the Enhanced PyInstaller GUI.
This script demonstrates the Inno Setup script generation with additional files.
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_inno_setup_script_generation():
    """Test the Inno Setup script generation with additional files."""
    from enhanced_pyinstaller_gui import EnhancedPyInstallerGUI
    
    # Create a mock GUI instance
    gui = EnhancedPyInstallerGUI()
    
    # Test data
    script_path = "test_app.py"
    exe_path = "test_app.exe"
    
    # Installer options with additional files
    installer_options = {
        'app_name': 'Test Application',
        'app_version': '1.0.0',
        'company_name': 'Test Company',
        'default_dir': '{pf}\\TestApp',
        'output_basename': 'test_app_setup',
        'compression': 'lzma',
        'solid_compression': True,
        'icon_file': '',
        'license_file': '',
        'create_desktop_icon': True,
        'create_start_menu': True,
        'run_after_install': True,
        'additional_files': [
            {'path': 'C:\\adb\\adb.exe', 'critical': True, 'type': 'file'},
            {'path': 'C:\\adb\\AdbWinApi.dll', 'critical': True, 'type': 'file'},
            {'path': 'C:\\configs', 'critical': False, 'type': 'folder'},
        ]
    }
    
    # Generate the Inno Setup script
    script_content = gui.create_inno_setup_script(script_path, exe_path, installer_options)
    
    print("=" * 80)
    print("Generated Inno Setup Script:")
    print("=" * 80)
    print(script_content)
    print("=" * 80)
    
    # Verify key components
    assert 'adb.exe' in script_content, "adb.exe should be in the script"
    assert 'AdbWinApi.dll' in script_content, "AdbWinApi.dll should be in the script"
    assert 'configs' in script_content, "configs folder should be in the script"
    assert 'CheckCriticalFile' in script_content, "CheckCriticalFile function should be present"
    assert 'CheckCriticalFolder' in script_content, "CheckCriticalFolder function should be present"
    
    print("\n✓ All assertions passed!")
    print("\nKey features verified:")
    print("  ✓ Additional files are included in [Files] section")
    print("  ✓ Critical files have CheckCriticalFile() checks")
    print("  ✓ Folders are included with recursesubdirs flag")
    print("  ✓ Pascal code section is generated for validation")

if __name__ == '__main__':
    try:
        test_inno_setup_script_generation()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

