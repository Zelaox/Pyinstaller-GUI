# Enhanced PyInstaller GUI

A modern graphical user interface for PyInstaller that simplifies the process of converting Python scripts to standalone executables with integrated installer creation.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ⚠️ Project Status & Disclaimer

**Important Notice:** This project is currently in active development and **everything may not work as intended**. Some features might be:
- Partially implemented
- Untested or buggy
- Redundant or overlapping with other features
- Subject to breaking changes

Use this tool at your own risk, and always test your generated executables thoroughly before distribution.

## 🎯 Features

### Core Functionality
- **Drag & Drop Support** - Easy file addition via drag and drop
- **PyInstaller Integration** - Convert Python scripts to executables
- **Inno Setup Integration** - Create professional Windows installers
- **Configuration Profiles** - Save and reuse your build settings
- **Batch Conversion** - Convert multiple Python files at once
- **Modern UI** - Light and dark theme support

### Advanced Features (⚠️ May Not Work Properly)
- **Additional Files Support** (NEW) - Include extra files/folders with your installer (e.g., ADB tools, config files)
  - Mark files as Critical (required) or Optional
  - Automatic validation during installation
  - ⚠️ Note: This feature is newly implemented and may have issues
- **Async File Operations** - Background file processing (may be redundant)
- **Update Manager** - Check for application updates (untested)
- **Custom Icon Support** - Set custom icons for your executable
- **Console/Window Mode** - Choose between console or windowed application

## 📋 Requirements

- Python 3.7 or higher
- PyQt5
- PyInstaller
- Inno Setup Compiler (optional, for creating installers)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Zelaox/Pyinstaller-GUI.git
cd Pyinstaller-GUI
```

2. Install required Python packages:
```bash
pip install PyQt5 pyinstaller
```

3. (Optional) Install Inno Setup for creating Windows installers:
   - Download from [Inno Setup Website](https://jrsoftware.org/isdl.php)
   - Install to default location or add to PATH

## 🔐 Administrator Privileges

**IMPORTANT:** This application requires Administrator privileges to function properly, especially when:
- Creating executables in protected directories (like Program Files)
- Installing packages or tools
- Modifying system-level settings

### Why Admin Rights Are Needed

The error `[WinError 5] Access Denied` occurs when trying to write to protected directories without admin rights. This tool:
- **Always requests admin privileges** for the installer (via Inno Setup)
- Allows you to **optionally require admin** for your converted executables

### Running with Admin Privileges

**Option 1: Run the GUI with Admin Rights**
- Right-click `enhanced_pyinstaller_gui.py` or the built executable
- Select "Run as administrator"

**Option 2: Build the GUI with Permanent Admin Request**
- Run `build.bat` (no admin required to build)
- The resulting executable will request admin rights when launched

### Administrator Flag for Your Executables

When creating profiles or configuring builds, you can check:
- ☑️ **"Require Administrator privileges (UAC elevation)"**

This will make your converted executable request admin rights when launched, useful for:
- Programs that need to access system files
- Tools that modify the registry
- Applications requiring hardware access (e.g., ADB tools)

## 💻 Usage

### Basic Usage

1. Run the application:
```bash
python enhanced_pyinstaller_gui.py
```

2. Add Python files:
   - Drag and drop `.py` files into the application window
   - Or use the "Add Files" button to browse

3. Configure build options:
   - Choose between "One File" or "One Folder" mode
   - Toggle console window visibility
   - Add custom icon (optional)

4. Click "Create EXE" to build your executable

### Creating Installers

1. After creating an executable, click "Create Installer"
2. Configure installer options:
   - Application name and version
   - Company name
   - Installation directory
   - Desktop icon and start menu entries
   - License file and setup icon

3. **NEW: Add Additional Files** (⚠️ Experimental)
   - Click "Add Files" or "Add Folder" in the Additional Files section
   - Choose whether files are Critical or Optional
   - Critical files will cause installation to fail if missing
   - Optional files will install if present but won't block installation

4. Click OK to generate the Inno Setup script and compile the installer

## 🐛 Known Issues & Limitations

### Major Issues
- **Not fully tested** - Many features haven't been thoroughly tested in real-world scenarios
- **Error handling** - May crash or behave unexpectedly with invalid inputs
- **Additional files feature** - Newly implemented, may not work correctly in all cases
- **Async operations** - May be redundant and cause conflicts with synchronous operations
- **Cross-platform support** - Primarily designed for Windows, may not work on macOS/Linux

### Minor Issues
- Deprecation warnings from PyQt5 (harmless but annoying)
- Some UI elements may not scale properly on high-DPI displays
- Log files accumulate without cleanup
- Build artifacts remain in `build/` and `dist/` directories

### Code Quality Issues
- **Redundant code** - Some functionality may be duplicated across modules
- **Inconsistent patterns** - Mix of different coding styles and approaches
- **Missing documentation** - Not all functions and classes are properly documented
- **No unit tests** - The project lacks comprehensive testing

## 📁 Project Structure

```
├── enhanced_pyinstaller_gui.py  # Main application file
├── async_file_system.py         # Async file operations (possibly redundant)
├── batch_conversion.py          # Batch processing functionality
├── config_profiles.py           # Profile management
├── drag_drop_support.py         # Drag & drop widget
├── modern_stylesheet.py         # UI themes and styling
├── update_manager.py            # Update checking (untested)
├── version.json                 # Version information
├── logs/                        # Log files directory
├── build/                       # PyInstaller build artifacts
└── dist/                        # Output executables
```

## 🔧 Configuration Profiles

Profiles allow you to save and reuse build configurations:
- Click "Manage Profiles" to create, edit, or delete profiles
- Click "Select Profile" to load a saved configuration
- Default profile is created automatically on first run

## 🤝 Contributing

This project is open for contributions! Given its current state, there are plenty of opportunities to:
- Fix bugs and issues
- Improve documentation
- Add proper unit tests
- Refactor redundant code
- Enhance existing features
- Add new features

Please feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

- GitHub: [@Zelaox](https://github.com/Zelaox)
- Email: Ferrari.kim@hotmail.com

## 🙏 Acknowledgments

- PyInstaller team for the excellent Python packaging tool
- PyQt5 for the GUI framework
- Inno Setup for the installer compiler
- All contributors and testers

## ⚠️ Final Warning

**USE AT YOUR OWN RISK!** This software is provided "as is" without warranty of any kind. Always test your executables and installers in a safe environment before distributing them to end users. The author is not responsible for any issues, data loss, or damages resulting from the use of this software.

---

**Note:** If you encounter issues or have suggestions for improvements, please open an issue on GitHub. Bug reports and feature requests are welcome!

