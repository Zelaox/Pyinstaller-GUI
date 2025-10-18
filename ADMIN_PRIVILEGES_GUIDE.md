# Administrator Privileges Guide

## Overview

This guide explains how the Enhanced PyInstaller GUI handles administrator privileges and how to fix the `[WinError 5] Access Denied` error when creating executables in protected directories.

## The Problem

When trying to create executables in protected directories like `C:\Program Files`, Windows requires administrator privileges. Without them, you'll see:

```
PermissionError: [WinError 5] Åtkomst nekad: 'C:\\Program Files (x86)\\Pyinstaller\\dist\\YourApp.exe'
```

## Solutions Implemented

### 1. For the Enhanced PyInstaller GUI Itself

#### Option A: Run as Administrator (Quick Fix)
1. Right-click `enhanced_pyinstaller_gui.py` or the built `.exe`
2. Select **"Run as administrator"**
3. Confirm the UAC prompt

#### Option B: Build with Permanent Admin Request
1. Open Command Prompt or PowerShell (no admin required)
2. Navigate to the project directory
3. Run: `build.bat`
4. The resulting executable will **always** request admin rights when launched

**Note:** PyInstaller 7.0+ blocks building as admin. The build script runs as normal user, but the OUTPUT executable requests admin via the `--uac-admin` flag.

### 2. For Your Converted Executables

#### Using the Profile Editor

1. Open Enhanced PyInstaller GUI
2. Go to **Settings → Manage Profiles**
3. Edit or create a profile
4. Check the box: **☑️ "Require Administrator privileges (UAC elevation)"**
5. Save the profile
6. Use this profile when converting your Python scripts

This will add the `--uac-admin` flag to PyInstaller, making your executable request admin rights.

### 3. For Installers (Inno Setup)

The installer now **automatically requires admin privileges** with these settings:
```ini
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
```

This means:
- The installer will request admin rights
- Users can choose to install without admin (if they change the setting)
- Installation to Program Files will work correctly

## Technical Details

### Files Modified

1. **enhanced_pyinstaller_gui.py**
   - Added `--uac-admin` flag to PyInstaller commands
   - Added admin requirement to Inno Setup scripts

2. **config_profiles.py**
   - Added `require_admin` checkbox to profile editor
   - Saves/loads admin preference in profiles

3. **admin_manifest.xml** (NEW)
   - UAC manifest for Windows
   - Requests administrator execution level

4. **build.bat** (NEW)
   - Automated build script
   - Uses --uac-admin flag (no admin required to build)
   - Output executable requests admin when launched

5. **.gitignore** (NEW)
   - Prevents committing build artifacts
   - Excludes logs, cache, and temporary files

## When to Use Admin Privileges

### ✅ Use Admin Privileges When:
- Writing to `C:\Program Files` or other protected directories
- Accessing system-level hardware (USB, serial ports, ADB)
- Modifying registry keys
- Installing system services
- Accessing protected system files

### ❌ Don't Use Admin Privileges When:
- Creating simple GUI applications
- Working with user documents only
- Network-only applications
- When security is a concern (principle of least privilege)

## Best Practices

1. **Default Output Location**: Change PyInstaller output to a user directory:
   ```
   C:\Users\YourName\Documents\MyProjects\dist
   ```

2. **Test Without Admin First**: Always test if your app works without admin privileges before requiring them

3. **User Communication**: If your app requires admin, clearly communicate why in:
   - Installer prompts
   - Application documentation
   - Error messages

4. **Development vs Production**:
   - Development: Run as regular user, output to user directories
   - Production: Build with admin if needed, test thoroughly

## Troubleshooting

### Problem: "This app requires administrator privileges"
**Solution**: Right-click and "Run as administrator"

### Problem: Build script fails with PyInstaller admin warning
**Solution**: Run `build.bat` as a normal user (NOT as administrator). PyInstaller 7.0+ blocks admin builds. The `--uac-admin` flag makes the OUTPUT exe request admin, not the build process.

### Problem: Installer won't run
**Solution**: The installer requires admin by default. Right-click → "Run as administrator"

### Problem: Still getting Access Denied
**Solutions**:
1. Check antivirus isn't blocking the operation
2. Verify the directory isn't locked by another program
3. Try a different output directory
4. Check disk permissions

## Security Considerations

⚠️ **Important**: Applications running with admin privileges have full system access. This means:

- **Malware Risk**: If compromised, admin apps can damage the entire system
- **User Responsibility**: Users should only grant admin to trusted applications
- **Code Review**: Always review your code before building with admin privileges
- **Minimal Scope**: Only request admin if absolutely necessary

## Example: Building an ADB Tool

If you're creating a tool that uses ADB (Android Debug Bridge):

1. ☑️ Check "Require Administrator privileges" in your profile
2. Add ADB files using "Additional Files" feature
3. Mark ADB files as "Critical"
4. Build your executable
5. Create installer (will request admin automatically)

The resulting installer will:
- Request admin rights
- Install to Program Files (or user-chosen location)
- Include all ADB files
- Create a shortcut that runs with admin privileges

## Summary

The Enhanced PyInstaller GUI now provides complete control over administrator privileges:

- ✅ Run the GUI with admin rights
- ✅ Build executables that request admin
- ✅ Create installers that require admin
- ✅ Proper UAC manifest integration
- ✅ Fixes `[WinError 5]` Access Denied errors

For questions or issues, please open an issue on GitHub: https://github.com/Zelaox/Pyinstaller-GUI/issues

