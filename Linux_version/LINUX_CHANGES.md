# Linux Version - Changes from Windows Version

## Summary of Changes

This document lists all the changes made to adapt the Enhanced PyInstaller GUI for Linux.

### Files Modified

1. **enhanced_pyinstaller_gui.py**
   - Removed `--uac-admin` flag (Windows-specific UAC elevation)
   - Removed Inno Setup installer integration
   - Updated path handling to be cross-platform
   - Removed Windows-specific manifest references

2. **config_profiles.py**
   - Removed "Require Administrator privileges" checkbox
   - Removed UAC-related options from profiles

### Files Removed

1. **admin_manifest.xml** - Windows UAC manifest (not needed on Linux)
2. **build_with_admin.bat** - Windows batch script
3. **ADMIN_PRIVILEGES_GUIDE.md** - Windows admin guide

### Features Removed

- ❌ UAC/Administrator privileges support (Windows-only)
- ❌ Inno Setup installer creation (Windows-only)
- ❌ Windows-specific admin manifest

### Features Kept

- ✅ PyInstaller integration (works on Linux)
- ✅ Drag & drop support
- ✅ Configuration profiles
- ✅ Batch conversion
- ✅ Additional files support
- ✅ Modern UI with themes
- ✅ Custom icons (PNG format recommended)

### New Features for Linux

- ✅ Shell script launcher (`run_gui.sh`)
- ✅ Automatic dependency checking
- ✅ Linux-specific documentation
- ✅ Cross-platform path handling

## How to Use on Linux

### Installation

```bash
cd Linux_version
chmod +x run_gui.sh
./run_gui.sh
```

Or directly:

```bash
python3 enhanced_pyinstaller_gui.py
```

### Creating Executables

The process is the same as Windows, but without installer creation:

1. Add your Python files
2. Configure options
3. Click "Create EXE"
4. Find your executable in `dist/`
5. Make it executable: `chmod +x dist/your_app`

### File Permissions

Unlike Windows, you don't need admin rights to create executables. They're created in your user directory with normal permissions.

If your app needs root access, users should run:
```bash
sudo ./your_app
```

## Technical Details

### Path Handling

The Linux version uses `os.path` for cross-platform compatibility, but defaults to forward slashes.

### Installer Creation

Since Inno Setup is Windows-only, the "Create Installer" feature is disabled on Linux. Future versions may add:
- AppImage creation
- DEB package creation
- RPM package creation
- Flatpak support

### Icons

Linux executables use PNG or SVG icons, not ICO files. The GUI will work with PNG icons.

## Building from Source

If you want to create a standalone executable of the GUI itself on Linux:

```bash
pyinstaller --onefile \
    --windowed \
    --name "Enhanced_PyInstaller_GUI" \
    enhanced_pyinstaller_gui.py
```

The executable will be in `dist/Enhanced_PyInstaller_GUI`

## Future Improvements

Planned features for the Linux version:

1. **AppImage Support** - Create AppImages for easy distribution
2. **DEB Packaging** - Create .deb packages for Debian/Ubuntu
3. **RPM Packaging** - Create .rpm packages for Fedora/RHEL
4. **Flatpak Support** - Package as Flatpak
5. **Desktop Integration** - Automatic .desktop file creation
6. **Theme Integration** - Better integration with system themes

## Known Limitations

1. **No installer creation** - Inno Setup is Windows-only
2. **Limited testing** - Only tested on Ubuntu 20.04/22.04
3. **Icon format** - ICO files may not work, use PNG
4. **Dependencies** - Some Python packages need system libraries

## Compatibility

Tested on:
- ✅ Ubuntu 20.04 LTS
- ✅ Ubuntu 22.04 LTS
- ⚠️ Debian 11 (should work)
- ⚠️ Fedora 36+ (should work)
- ⚠️ Arch Linux (should work)
- ❌ Other distributions (untested)

## Contributing

If you test on other distributions, please report:
- Distribution name and version
- Issues encountered
- Solutions found

## Questions?

See README_LINUX.md for more information or open an issue on GitHub.

