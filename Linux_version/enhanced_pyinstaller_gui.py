#!/usr/bin/env python3
"""
Main module for the enhanced PyInstaller GUI application - Linux Version
This module integrates all the enhancements including modern UI, drag & drop support,
asynchronous file system operations, batch conversion, and configuration profiles.

Linux-specific changes:
- Removed Windows UAC/admin privileges
- Disabled Inno Setup installer creation (Windows-only)
- Added shebang for direct execution
"""

import sys
import os
import platform
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Platform detection for Linux-specific behavior
IS_LINUX = platform.system() == 'Linux'
IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QTextEdit, QMessageBox, QLabel, QProgressBar, 
    QDialog, QCheckBox, QLineEdit, QHBoxLayout, QDialogButtonBox, 
    QTabWidget, QSlider, QAction, QInputDialog, QComboBox, 
    QListWidget, QListWidgetItem, QSplitter, QMenu,
    QToolBar, QStatusBar, QFrame,
    QScrollArea, QProgressDialog, QAbstractItemView
)
from PyQt5.QtCore import (
    QThread, pyqtSignal, QObject, QProcess, Qt, QTimer, 
    QSettings, QSize, QPoint, QEvent, QMimeData, QUrl, QRect
)
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent, QPixmap

# Import enhanced modules
from modern_stylesheet import StyleManager, LIGHT_STYLESHEET, DARK_STYLESHEET, ICONS
from drag_drop_support import DragDropListWidget
from async_file_system import FileSystemManager, AsyncFileProcessor
from batch_conversion import BatchConversionManager
from config_profiles import ProfileManager, ProfileSelectionDialog, ConfigProfile
import update_manager

# Setup logging
def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger with file and console handlers."""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file_path = os.path.join(logs_dir, log_file)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_path)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create loggers
app_logger = setup_logger('app', 'pyinstaller_gui.log')
conversion_logger = setup_logger('conversion', 'conversion.log')

class PyInstallerThread(QThread):
    """Thread for executing PyInstaller commands without blocking the UI."""
    progress_signal = pyqtSignal(int)
    message_signal = pyqtSignal(str)
    
    def __init__(self, command):
        """
        Initialize the PyInstaller thread.
        
        Args:
            command: PyInstaller command to execute
        """
        super().__init__()
        self.command = command
        
    def run(self):
        """Execute the PyInstaller command."""
        try:
            import subprocess
            
            # Start the process
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            # Simulate phases with progress
            phases = [
                (20, "Analyzing imports..."),
                (40, "Collecting modules..."),
                (60, "Building EXE..."),
                (80, "Finalizing package...")
            ]
            
            for progress, message in phases:
                # Check if process is still running
                if process.poll() is not None:
                    break
                
                # Update progress and status
                self.progress_signal.emit(progress)
                self.message_signal.emit(message)
                
                # Wait a bit before next check
                self.sleep(2)
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            # Check result
            if process.returncode == 0:
                self.progress_signal.emit(100)
                self.message_signal.emit("Conversion completed successfully")
            else:
                self.message_signal.emit(f"Conversion failed: {stderr}")
                
        except Exception as e:
            self.message_signal.emit(f"Error: {str(e)}")





class EnhancedPyInstallerGUI(QMainWindow):
    """
    Enhanced PyInstaller GUI with modern UI, drag & drop support,
    asynchronous file system operations, batch conversion, and configuration profiles.
    """
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("Enhanced PyInstaller GUI")
        self.resize(1000, 700)
        
        # Initialize output_text early to prevent AttributeError
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # Initialize settings
        self.settings = QSettings("PyInstallerGUI", "EnhancedPyInstallerGUI")
        self.auto_check_updates = self.settings.value("AutoCheckUpdates", True, type=bool)
        
        # Initialize profile manager and current profile
        self.profile_manager = ProfileManager()
        self.current_profile = None
        
        # Create style manager
        self.style_manager = StyleManager()
        
        # Initialize properties
        self.file_system_manager = FileSystemManager()
        self.batch_manager = BatchConversionManager(self)
        self.async_processor = AsyncFileProcessor()
        
        # Create the UI
        self.initUI()
        
        # Load last used profile
        self.load_default_profile()
        
        # Apply saved theme
        self.apply_saved_theme()
        
        # Schedule update check if enabled
        if self.auto_check_updates:
            QTimer.singleShot(2000, self.silent_check_for_updates)
    
    def initUI(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Enhanced PyInstaller GUI")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Create splitter for files list and output
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Files section
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        
        files_header = QHBoxLayout()
        files_label = QLabel("Python Scripts")
        files_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        files_header.addWidget(files_label)
        
        files_layout.addLayout(files_header)
        
        # Create drag & drop list widget with enhanced configuration
        self.files_list = DragDropListWidget(self, ['.py', '.pyw'])
        # Explicitly ensure drag & drop is configured correctly
        self.files_list.setAcceptDrops(True)
        self.files_list.setDragDropMode(QAbstractItemView.DropOnly)
        # Log initialization
        self.log_message("Initializing file list with drag & drop support")
        files_layout.addWidget(self.files_list)
        
        # Add files section to splitter
        splitter.addWidget(files_widget)
        
        # Output section
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        output_header = QHBoxLayout()
        output_label = QLabel("Output")
        output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        output_header.addWidget(output_label)
        
        # Clear output button
        clear_output_button = QPushButton("Clear")
        clear_output_button.clicked.connect(self.clear_output)
        output_header.addWidget(clear_output_button)
        
        output_layout.addLayout(output_header)
        
        # Output text area - use existing output_text that was initialized in __init__
        output_layout.addWidget(self.output_text)
        
        # Add output section to splitter
        splitter.addWidget(output_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 400])
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        add_files_action = QAction("Add Files", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self.add_files)
        file_menu.addAction(add_files_action)
        
        package_action = QAction("Package Selected", self)
        package_action.setShortcut("Ctrl+P")
        package_action.triggered.connect(self.package_selected)
        file_menu.addAction(package_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        
        # Theme submenu
        theme_menu = settings_menu.addMenu("Theme")
        
        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        matrix_theme_action = QAction("Matrix", self)
        matrix_theme_action.triggered.connect(lambda: self.change_theme("matrix"))
        theme_menu.addAction(matrix_theme_action)
        
        # Profile management
        profile_action = QAction("Manage Profiles", self)
        profile_action.triggered.connect(self.manage_profiles)
        settings_menu.addAction(profile_action)
        
        select_profile_action = QAction("Select Profile", self)
        select_profile_action.triggered.connect(self.select_profile)
        settings_menu.addAction(select_profile_action)
        
        # Auto-update check option
        settings_menu.addSeparator()
        
        auto_update_action = QAction("Auto Check Updates", self)
        auto_update_action.setCheckable(True)
        auto_update_action.setChecked(self.auto_check_updates)
        auto_update_action.triggered.connect(self.toggle_auto_update_checks)
        settings_menu.addAction(auto_update_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        update_action = QAction("Check for Updates", self)
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        return toolbar
    
    def add_files(self):
        """Add files to the list using the file dialog."""
        try:
            # Log the action for debugging
            self.log_message("Opening file dialog to add Python files")
            
            # Use the standard file dialog to select Python files
            file_filter = "Python Files (*.py *.pyw);;All Files (*.*)"
            files, _ = QFileDialog.getOpenFileNames(self, "Add Python Scripts", "", file_filter)
            
            # Process the selected files
            if files:
                added_count = 0
                for file_path in files:
                    # Validate file extension
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() in ['.py', '.pyw']:
                        # Check if file already exists in the list
                        items = self.files_list.findItems(file_path, Qt.MatchExactly)
                        if not items:
                            self.files_list.addItem(file_path)
                            added_count += 1
                
                # Log the results
                self.log_message(f"Added {added_count} Python files via dialog")
                
                # Update status message
                if added_count > 0:
                    self.status_bar.showMessage(f"Added {added_count} files", 3000)
                else:
                    self.status_bar.showMessage("No valid Python files were selected", 3000)
            else:
                self.log_message("File dialog canceled or no files selected")
        
        except Exception as e:
            # Log any errors that occur
            self.log_message(f"Error adding files: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred while adding files: {str(e)}")
            
        # Alternative method to try if the custom widget's method fails
        # self.files_list.add_files_dialog()
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.clear()
    
    def package_selected(self):
        """Package the selected script."""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a script to package.")
            return
        
        script_path = selected_items[0].text()
        
        # Use the current profile or select one
        if not self.current_profile:
            self.select_profile()
            if not self.current_profile:
                return
        
        # Log the packaging operation
        self.log_message(f"Packaging {script_path} with profile {self.current_profile.name}")
        
        # Create a command based on the profile
        cmd = self.create_pyinstaller_command(script_path, self.current_profile.options)
        
        # Show the command in the output
        self.log_message(f"Command: {' '.join(cmd)}")
        
        # Disable UI controls during conversion
        self.progress_bar.setValue(0)
        
        # Execute the command in a separate thread
        self.pyinstaller_thread = PyInstallerThread(cmd)
        self.pyinstaller_thread.progress_signal.connect(self.update_progress)
        self.pyinstaller_thread.message_signal.connect(self.log_message)
        self.pyinstaller_thread.finished.connect(self.on_packaging_finished)
        self.pyinstaller_thread.start()
    
    def create_pyinstaller_command(self, script_path, options):
        """
        Create a PyInstaller command based on the options.
        
        Args:
            script_path: Path to the script
            options: Configuration options
            
        Returns:
            list: Command as a list of strings
        """
        cmd = ["pyinstaller"]
        
        # Add basic options
        if options.get("onefile", True):
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        if options.get("console_mode", False):
            cmd.append("--console")
        else:
            cmd.append("--windowed")
        
        # Add icon if specified
        icon_path = options.get("icon_path")
        if icon_path and os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
        
        # Add output directory if specified
        output_dir = options.get("output_dir")
        if output_dir:
            cmd.extend(["--distpath", output_dir])
        
        # Add clean build option
        if options.get("clean_build", True):
            cmd.append("--clean")
        
        # Add UPX compression option
        if options.get("upx_compress", False):
            cmd.append("--upx-dir=upx")
        
        # Note: --uac-admin removed for Linux version (Windows-only)
        # Linux users should use 'sudo' if root access is needed
        
        # Add debug option - with proper value
        if options.get("debug", False):
            cmd.extend(["-d", "all"])  # Use "-d all" instead of "--debug"
        
        # Add hidden imports
        for imp in options.get("hidden_imports", []):
            cmd.extend(["--hidden-import", imp])
        
        # Add data files
        for src, dst in options.get("data_files", []):
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
        
        # Add binary files
        for src, dst in options.get("binary_files", []):
            cmd.extend(["--add-binary", f"{src}{os.pathsep}{dst}"])
        
        # Add exclude modules
        for mod in options.get("exclude_modules", []):
            cmd.extend(["--exclude-module", mod])
        
        # Add the script path
        cmd.append(script_path)
        
        return cmd
    
    def on_packaging_finished(self):
        """Handle the completion of packaging."""
        self.progress_bar.setValue(100)
        self.log_message("Packaging completed!")
    
    def manage_profiles(self):
        """Open the profile management dialog."""
        try:
            dialog = ProfileManagementDialog(self.profile_manager, self)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Refresh current profile in case it was modified
                if self.current_profile:
                    self.current_profile = self.profile_manager.get_profile(self.current_profile.name)
                    if not self.current_profile:
                        # Current profile was deleted, load default
                        self.current_profile = self.profile_manager.get_default_profile()
                        if self.current_profile:
                            self.log_message(f"Loaded default profile: {self.current_profile.name}")
                            self.statusBar().showMessage(f"Profile: {self.current_profile.name}", 3000)
        except Exception as e:
            self.log_message(f"Error opening profile management dialog: {str(e)}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(self, "Error", f"Failed to open profile management dialog:\n{str(e)}")
    
    def select_profile(self):
        """Open the profile selection dialog."""
        dialog = ProfileSelectionDialog(self.profile_manager, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted and dialog.selected_profile:
            self.current_profile = dialog.selected_profile
            self.log_message(f"Selected profile: {self.current_profile.name}")
            self.statusBar().showMessage(f"Profile: {self.current_profile.name}", 3000)
            return True
        
        return False
    
    def show_about(self):
        """Show the About dialog."""
        platform_info = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()
        
        QMessageBox.about(
            self,
            "About Enhanced PyInstaller GUI - Linux Version",
            f"""
            <h2>Enhanced PyInstaller GUI</h2>
            <h3>🐧 Linux Version</h3>
            <p>A modern graphical interface for PyInstaller</p>
            <p><b>Version:</b> 1.0.0-linux</p>
            <p><b>Platform:</b> {platform_info}</p>
            <p><b>Python:</b> {python_version}</p>
            <p>© 2023-2025</p>
            <p>This application simplifies the process of converting Python scripts to standalone executables on Linux.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Modern user interface with dark mode support</li>
                <li>Drag and drop support for Python files</li>
                <li>Configuration profiles for reusing settings</li>
                <li>Batch conversion for multiple files</li>
                <li>Additional files support</li>
                <li>Cross-platform compatible code</li>
            </ul>
            <p><b>Linux-Specific Notes:</b></p>
            <ul>
                <li>No admin privileges required (use sudo if needed)</li>
                <li>Installer creation disabled (Windows-only)</li>
                <li>Use PNG icons instead of ICO</li>
            </ul>
            <p><b>GitHub:</b> <a href="https://github.com/Zelaox/Pyinstaller-GUI">Zelaox/Pyinstaller-GUI</a></p>
            """
        )

    def change_theme(self, theme):
        """
        Change the application theme.
        
        Args:
            theme: Theme name ("light", "dark", or "matrix")
        """
        app = QApplication.instance()
        self.style_manager.apply_stylesheet(app, theme)
        self.log_message(f"Theme changed to {theme}")

    def log_message(self, message):
        """Log a message to the output text area."""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.output_text.append(f"[{timestamp}] {message}")
        
        # Scroll to bottom
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
        
        # Also log to file
        app_logger.info(message)

    def update_progress(self, progress):
        """Update the progress bar."""
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.log_message("Conversion completed!")
        elif progress % 20 == 0:  # Log at 0, 20, 40, 60, 80
            self.log_message(f"Progress: {progress}%")

    def apply_saved_theme(self):
        """Apply the theme saved in settings."""
        theme = self.settings.value("Theme", "light")
        self.change_theme(theme)
    
    def silent_check_for_updates(self):
        """Silently check for updates without user interaction unless an update is available."""
        try:
            # Check for updates but don't show progress dialog
            update_available = update_manager.check_for_updates(self)
            # If no update was applied, we don't need to show anything
            # If an update was applied, the update_manager has already shown a message
        except Exception as e:
            # Log the error but don't show to user in silent mode
            self.log_message(f"Silent update check failed: {str(e)}")

    # Add a method to toggle automatic update checks
    def toggle_auto_update_checks(self, enabled):
        """Enable or disable automatic update checks at startup."""
        self.auto_check_updates = enabled
        self.settings.setValue("AutoCheckUpdates", enabled)
        self.log_message(f"Automatic update checks {'enabled' if enabled else 'disabled'}")

    def check_for_updates(self):
        """Check for updates with user interaction."""
        try:
            # Import here to handle potential import errors gracefully
            import update_manager
            update_available = update_manager.check_for_updates(self)
            if not update_available:
                QMessageBox.information(self, "Update Check", "No updates available. You have the latest version.")
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"Error checking for updates: {str(e)}")
            self.log_message(f"Update check failed: {str(e)}")

    def load_default_profile(self):
        """Load the default configuration profile."""
        try:
            self.current_profile = self.profile_manager.get_default_profile()
            if self.current_profile:
                self.log_message(f"Loaded profile: {self.current_profile.name}")
                self.statusBar().showMessage(f"Profile: {self.current_profile.name}", 3000)
            else:
                self.log_message("No default profile found. Creating a basic profile.")
                # Create a basic default profile
                default_profile = ConfigProfile(
                    name="Default",
                    options={
                        "onefile": True,
                        "console_mode": False,
                        "icon_path": "",
                        "output_dir": "dist",
                        "clean_build": True,
                        "upx_compress": False,
                        "debug": False,
                        "hidden_imports": [],
                        "data_files": [],
                        "binary_files": [],
                        "exclude_modules": []
                    }
                )
                self.profile_manager.add_profile(default_profile)
                self.profile_manager.set_default_profile(default_profile.name)
                self.current_profile = default_profile
                self.statusBar().showMessage("Created default profile", 3000)
        except Exception as e:
            self.log_message(f"Error loading default profile: {str(e)}")
            # Create a minimal fallback profile
            self.current_profile = ConfigProfile(
                name="Fallback",
                options={"onefile": True, "console_mode": False}
            )

    def update_batch_progress(self, progress):
        """Update the batch progress."""
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.log_message("Batch conversion completed.")
        elif progress % 20 == 0:  # Log at 0, 20, 40, 60, 80
            self.log_message(f"Batch progress: {progress}%")

    def update_script_progress(self, script_path, progress):
        """Update the script progress."""
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.log_message(f"[{os.path.basename(script_path)}] Conversion completed.")
        elif progress % 20 == 0:  # Log at 0, 20, 40, 60, 80
            self.log_message(f"[{os.path.basename(script_path)}] Progress: {progress}%")

    def update_script_status(self, status):
        """Update the script status."""
        self.log_message(status)
        self.status_bar.showMessage(status, 3000)

    def on_batch_completed(self, result):
        """Handle batch completion."""
        self.log_message(f"Batch conversion completed with result: {result}")
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Batch Conversion", f"Batch conversion completed: {result}")

# Main entry point
if __name__ == "__main__":
    try:
        # Platform check and info
        print("=" * 60)
        print("Enhanced PyInstaller GUI - Linux Version")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        
        if not IS_LINUX and not IS_MACOS:
            print("\nWARNING: This is the Linux version!")
            print("For Windows, please use the version in the parent directory.")
            print("=" * 60)
        
        print("\nStarting application...")
        print("=" * 60)
        
        app = QApplication(sys.argv)
        main_window = EnhancedPyInstallerGUI()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        app_logger.error(f"Application error: {e}")
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)