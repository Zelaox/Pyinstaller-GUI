# Enhanced PyInstaller GUI - Linux Version

A modern graphical user interface for PyInstaller on Linux that simplifies the process of converting Python scripts to standalone executables.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)

## ⚠️ Project Status & Disclaimer

**Important Notice:** This is the Linux-adapted version of Enhanced PyInstaller GUI. It is currently in active development and **everything may not work as intended**. Some features might be:
- Partially implemented
- Untested on all Linux distributions
- Subject to breaking changes

Use this tool at your own risk, and always test your generated executables thoroughly before distribution.

## 🎯 Features

### Core Functionality
- **Drag & Drop Support** - Easy file addition via drag and drop
- **PyInstaller Integration** - Convert Python scripts to executables
- **Configuration Profiles** - Save and reuse your build settings
- **Batch Conversion** - Convert multiple Python files at once
- **Modern UI** - Light and dark theme support

### Linux-Specific Changes
- ✅ Removed Windows UAC/Admin privileges code
- ✅ Removed Inno Setup integration (Windows-only)
- ✅ Cross-platform path handling
- ✅ Works with standard Linux permissions
- ⚠️ Linux packaging (.deb, .rpm) support - Coming soon!

### Advanced Features
- **Additional Files Support** - Include extra files/folders with your executable
- **Custom Icon Support** - Set custom icons for your executable
- **Console/Window Mode** - Choose between console or windowed application
- **Batch Processing** - Convert multiple files at once

## 📋 Requirements

- Python 3.7 or higher
- PyQt5
- PyInstaller
- Linux OS (tested on Ubuntu, should work on most distributions)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Zelaox/Pyinstaller-GUI.git
cd Pyinstaller-GUI/Linux_version
```

2. Install required Python packages:
```bash
pip install PyQt5 pyinstaller
```

Or using pip3:
```bash
pip3 install PyQt5 pyinstaller
```

3. Make the script executable (optional):
```bash
chmod +x enhanced_pyinstaller_gui.py
```

## 💻 Usage

### Basic Usage

1. Run the application:
```bash
python3 enhanced_pyinstaller_gui.py
```

Or if made executable:
```bash
./enhanced_pyinstaller_gui.py
```

2. Add Python files:
   - Drag and drop `.py` files into the application window
   - Or use the "Add Files" button to browse

3. Configure build options:
   - Choose between "One File" or "One Folder" mode
   - Toggle console window visibility
   - Add custom icon (optional)

4. Click "Create EXE" to build your executable

### Adding Additional Files

1. After creating an executable, you can include additional files
2. Click "Add Files" or "Add Folder" in the Additional Files section
3. Mark files as Critical or Optional:
   - **Critical** - Required for the application to run
   - **Optional** - Nice to have but not required

### Configuration Profiles

Profiles allow you to save and reuse build configurations:
- Click "Manage Profiles" to create, edit, or delete profiles
- Click "Select Profile" to load a saved configuration
- Default profile is created automatically on first run

## 🔧 Linux-Specific Notes

### File Permissions

Unlike Windows, Linux executables don't require special administrator privileges for most operations. However:

- Executables created by PyInstaller need execute permissions:
  ```bash
  chmod +x dist/your_app
  ```

- If your app needs root privileges, users should run:
  ```bash
  sudo ./your_app
  ```

### Output Location

By default, PyInstaller creates executables in:
```
./dist/your_app
```

This works fine on Linux without special permissions. No need for admin rights like on Windows!

### Desktop Integration

To create a desktop shortcut for your application:

1. Create a `.desktop` file in `~/.local/share/applications/`:
```bash
nano ~/.local/share/applications/your_app.desktop
```

2. Add the following content:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Your App Name
Comment=Your app description
Exec=/path/to/your/app
Icon=/path/to/your/icon.png
Terminal=false
Categories=Utility;
```

3. Make it executable:
```bash
chmod +x ~/.local/share/applications/your_app.desktop
```

## 🐛 Known Issues & Limitations

### Linux-Specific Issues
- **AppImage creation** - Not yet implemented
- **DEB/RPM packaging** - Not yet implemented
- **Icon formats** - Linux prefers .png or .svg, .ico files may not work
- **Theme integration** - May not match your desktop theme perfectly

### General Issues
- **Not fully tested** - Limited testing on different Linux distributions
- **Dependencies** - Some Python packages may require system libraries
- **Error handling** - May crash with invalid inputs
- **No unit tests** - The project lacks comprehensive testing

## 📁 Project Structure

```
Linux_version/
├── enhanced_pyinstaller_gui.py  # Main application file
├── async_file_system.py         # Async file operations
├── batch_conversion.py          # Batch processing functionality
├── config_profiles.py           # Profile management
├── drag_drop_support.py         # Drag & drop widget
├── modern_stylesheet.py         # UI themes and styling
├── update_manager.py            # Update checking
├── version.json                 # Version information
└── logs/                        # Log files directory
```

## 🤝 Contributing

Contributions are welcome! Areas that need work:
- Testing on different Linux distributions
- AppImage/Flatpak packaging support
- DEB/RPM package creation
- Better icon handling for Linux
- Desktop environment integration

## 📦 Building AppImages (Future Feature)

We plan to add AppImage support for easy distribution:

```bash
# Coming soon!
python3 enhanced_pyinstaller_gui.py --create-appimage your_script.py
```

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'PyQt5'"
**Solution**: Install PyQt5:
```bash
pip3 install PyQt5
```

### Problem: "Permission denied" when running executable
**Solution**: Add execute permission:
```bash
chmod +x dist/your_app
```

### Problem: Missing system libraries
**Solution**: Install required development libraries:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libx11-dev libxext-dev

# Fedora/RHEL
sudo dnf install python3-devel libX11-devel libXext-devel

# Arch
sudo pacman -S python libx11 libxext
```

### Problem: Icon not showing
**Solution**: Use PNG format instead of ICO:
```bash
convert icon.ico icon.png
```

## 📞 Contact

- GitHub: [@Zelaox](https://github.com/Zelaox)
- Email: Ferrari.kim@hotmail.com

## 🙏 Acknowledgments

- PyInstaller team for the excellent Python packaging tool
- PyQt5 for the GUI framework
- Linux community for testing and feedback

## ⚠️ Final Warning

**USE AT YOUR OWN RISK!** This software is provided "as is" without warranty of any kind. Always test your executables thoroughly before distributing them to end users.

---

**Note:** This is the Linux-adapted version. For Windows, see the main README.md file in the parent directory.

