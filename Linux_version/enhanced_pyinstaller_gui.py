"""
Main module for the enhanced PyInstaller GUI application.
This module integrates all the enhancements including modern UI, drag & drop support,
asynchronous file system operations, batch conversion, and configuration profiles.
"""

import sys
import os
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QTextEdit, QMessageBox, QLabel, QProgressBar, 
    QDialog, QCheckBox, QLineEdit, QHBoxLayout, QDialogButtonBox, 
    QTabWidget, QSlider, QAction, QInputDialog, QComboBox, 
    QListWidget, QListWidgetItem, QSplitter, QGroupBox, QFormLayout, QMenu,
    QToolBar, QStatusBar, QFrame, QTreeWidget, QTreeWidgetItem,
    QScrollArea, QProgressDialog, QAbstractItemView, QRadioButton
)
from PyQt5.QtCore import (
    QThread, pyqtSignal, QObject, QProcess, Qt, QTimer, 
    QSettings, QSize, QPoint, QEvent, QMimeData, QUrl, QRect
)
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent, QPixmap, QKeySequence, QColor

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

class InnoSetupWorker(QObject):
    """Worker for running Inno Setup compiler in a separate thread."""
    progress_signal = pyqtSignal(int)
    message_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, command):
        """
        Initialize the Inno Setup worker.
        
        Args:
            command: Command to execute to compile the installer
        """
        super().__init__()
        self.command = command
        
    def run(self):
        """Run the Inno Setup compiler."""
        try:
            import subprocess
            
            # Update progress
            self.progress_signal.emit(90)
            self.message_signal.emit("Compiling installer...")
            
            # Start the process
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            # Check result
            if process.returncode == 0:
                self.progress_signal.emit(100)
                self.message_signal.emit("Installer compiled successfully")
                self.finished_signal.emit(True, "Success")
            else:
                self.message_signal.emit(f"Installer compilation failed: {stderr}")
                self.finished_signal.emit(False, stderr)
                
        except Exception as e:
            self.message_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, str(e))

class AdditionalFileDialog(QDialog):
    """Dialog for specifying whether an additional file is critical or optional."""
    
    def __init__(self, file_path, is_folder=False, existing_critical=None, parent=None):
        """
        Initialize the additional file dialog.
        
        Args:
            file_path: Path to the file or folder
            is_folder: Whether this is a folder (True) or file (False)
            existing_critical: If editing, the existing critical flag value
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.is_folder = is_folder
        self.is_critical = existing_critical if existing_critical is not None else True
        self.initUI()
        
    def initUI(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Additional File Options")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Display file/folder path
        path_label = QLabel(f"{'Folder' if self.is_folder else 'File'}: {os.path.basename(self.file_path)}")
        path_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(path_label)
        
        full_path_label = QLabel(f"Path: {self.file_path}")
        full_path_label.setWordWrap(True)
        layout.addWidget(full_path_label)
        
        layout.addSpacing(10)
        
        # Critical/Optional selection
        importance_group = QGroupBox("File Importance")
        importance_layout = QVBoxLayout()
        
        self.critical_radio = QRadioButton("Critical (Required)")
        self.critical_radio.setToolTip("Installation will fail if this file is missing")
        self.critical_radio.setChecked(self.is_critical)
        importance_layout.addWidget(self.critical_radio)
        
        self.optional_radio = QRadioButton("Optional")
        self.optional_radio.setToolTip("Installation will continue even if this file is missing")
        self.optional_radio.setChecked(not self.is_critical)
        importance_layout.addWidget(self.optional_radio)
        
        importance_group.setLayout(importance_layout)
        layout.addWidget(importance_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_result(self):
        """Get the result of the dialog."""
        return {
            'path': self.file_path,
            'critical': self.critical_radio.isChecked(),
            'type': 'folder' if self.is_folder else 'file'
        }

class InstallerOptionsDialog(QDialog):
    """Dialog for configuring installer options before creating the installer."""
    
    def __init__(self, app_name, profile, parent=None):
        """
        Initialize the installer options dialog.
        
        Args:
            app_name: Name of the application
            profile: Current profile
            parent: Parent widget
        """
        super().__init__(parent)
        self.app_name = app_name
        self.profile = profile
        self.options = {}
        self.additional_files = []  # List to store additional files
        self.initUI()
        self.loadOptions()
        
    def initUI(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Installer Options")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Application information
        app_group = QGroupBox("Application Information")
        app_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.app_name)
        app_layout.addRow("Application Name:", self.name_edit)
        
        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0.0")
        app_layout.addRow("Version:", self.version_edit)
        
        self.company_edit = QLineEdit()
        app_layout.addRow("Company Name:", self.company_edit)
        
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setText(f"{self.app_name}_setup")
        app_layout.addRow("Output Filename:", self.output_name_edit)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # Installation options
        install_group = QGroupBox("Installation Options")
        install_layout = QFormLayout()
        
        self.desktop_icon = QCheckBox("Create Desktop Icon")
        self.desktop_icon.setChecked(True)
        install_layout.addRow("", self.desktop_icon)
        
        self.start_menu = QCheckBox("Create Start Menu Entry")
        self.start_menu.setChecked(True)
        install_layout.addRow("", self.start_menu)
        
        self.install_dir_edit = QLineEdit()
        self.install_dir_edit.setText("{pf}\\{#MyAppName}")
        install_layout.addRow("Installation Directory:", self.install_dir_edit)
        
        self.license_file_edit = QLineEdit()
        license_browse_btn = QPushButton("Browse...")
        license_browse_btn.clicked.connect(lambda: self.browse_file(self.license_file_edit, "License File (*.txt *.rtf)"))
        license_layout = QHBoxLayout()
        license_layout.addWidget(self.license_file_edit)
        license_layout.addWidget(license_browse_btn)
        install_layout.addRow("License File:", license_layout)
        
        self.icon_file_edit = QLineEdit()
        icon_browse_btn = QPushButton("Browse...")
        icon_browse_btn.clicked.connect(lambda: self.browse_file(self.icon_file_edit, "Icon File (*.ico)"))
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_file_edit)
        icon_layout.addWidget(icon_browse_btn)
        install_layout.addRow("Setup Icon:", icon_layout)
        
        self.run_after_install = QCheckBox("Run Application After Installation")
        self.run_after_install.setChecked(True)
        install_layout.addRow("", self.run_after_install)
        
        install_group.setLayout(install_layout)
        layout.addWidget(install_group)
        
        # Compression options
        compression_group = QGroupBox("Compression Options")
        compression_layout = QFormLayout()
        
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["lzma", "zip", "bzip"])
        compression_layout.addRow("Compression Method:", self.compression_combo)
        
        self.solid_compression = QCheckBox("Use Solid Compression")
        self.solid_compression.setChecked(True)
        compression_layout.addRow("", self.solid_compression)
        
        compression_group.setLayout(compression_layout)
        layout.addWidget(compression_group)
        
        # Additional Files section
        files_group = QGroupBox("Additional Files")
        files_layout = QVBoxLayout()
        
        # Description label
        desc_label = QLabel("Include additional files/folders with the installer (e.g., ADB tools, config files)")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray; font-size: 9pt;")
        files_layout.addWidget(desc_label)
        
        # List widget to show added files
        self.additional_files_list = QListWidget()
        self.additional_files_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.additional_files_list.setMaximumHeight(150)
        files_layout.addWidget(self.additional_files_list)
        
        # Buttons for managing additional files
        buttons_layout = QHBoxLayout()
        
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_additional_files)
        buttons_layout.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_additional_folder)
        buttons_layout.addWidget(add_folder_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_additional_file)
        buttons_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected_additional_file)
        buttons_layout.addWidget(remove_btn)
        
        buttons_layout.addStretch()
        files_layout.addLayout(buttons_layout)
        
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def browse_file(self, line_edit, filter_text):
        """Open file browser and set selected file to line edit."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter_text)
        if file_path:
            line_edit.setText(file_path)
    
    def add_additional_files(self):
        """Add additional files to the installer."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Additional Files", "", "All Files (*.*)")
        
        for file_path in files:
            if file_path:
                # Show dialog to specify if file is critical or optional
                dialog = AdditionalFileDialog(file_path, is_folder=False, parent=self)
                if dialog.exec_() == QDialog.Accepted:
                    file_info = dialog.get_result()
                    self.additional_files.append(file_info)
                    self._update_additional_files_list()
    
    def add_additional_folder(self):
        """Add an additional folder to the installer."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Additional Folder")
        
        if folder_path:
            # Show dialog to specify if folder is critical or optional
            dialog = AdditionalFileDialog(folder_path, is_folder=True, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                folder_info = dialog.get_result()
                self.additional_files.append(folder_info)
                self._update_additional_files_list()
    
    def edit_additional_file(self):
        """Edit the selected additional file's critical/optional flag."""
        current_item = self.additional_files_list.currentRow()
        if current_item < 0 or current_item >= len(self.additional_files):
            QMessageBox.warning(self, "No Selection", "Please select a file to edit.")
            return
        
        file_info = self.additional_files[current_item]
        dialog = AdditionalFileDialog(
            file_info['path'], 
            is_folder=(file_info['type'] == 'folder'),
            existing_critical=file_info['critical'],
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            updated_info = dialog.get_result()
            self.additional_files[current_item] = updated_info
            self._update_additional_files_list()
    
    def remove_selected_additional_file(self):
        """Remove the selected additional file from the list."""
        current_item = self.additional_files_list.currentRow()
        if current_item < 0 or current_item >= len(self.additional_files):
            QMessageBox.warning(self, "No Selection", "Please select a file to remove.")
            return
        
        file_info = self.additional_files[current_item]
        reply = QMessageBox.question(
            self, 
            "Confirm Removal",
            f"Remove {os.path.basename(file_info['path'])} from additional files?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.additional_files[current_item]
            self._update_additional_files_list()
    
    def _update_additional_files_list(self):
        """Update the additional files list widget display."""
        self.additional_files_list.clear()
        
        for file_info in self.additional_files:
            file_name = os.path.basename(file_info['path'])
            file_type = "Folder" if file_info['type'] == 'folder' else "File"
            critical_status = "Critical" if file_info['critical'] else "Optional"
            
            display_text = f"[{critical_status}] {file_type}: {file_name}"
            item = QListWidgetItem(display_text)
            item.setToolTip(file_info['path'])
            
            # Color code by importance
            if file_info['critical']:
                item.setForeground(QColor(200, 50, 50))  # Red for critical
            else:
                item.setForeground(QColor(50, 150, 50))  # Green for optional
            
            self.additional_files_list.addItem(item)
    
    def loadOptions(self):
        """Load options from profile."""
        if not self.profile or not hasattr(self.profile, 'options'):
            return
            
        # Extract installer options from profile
        setup_options = self.profile.options.get('setup_options', {})
        
        # Set version
        if setup_options.get('version'):
            self.version_edit.setText(setup_options.get('version'))
            
        # Set company name
        if setup_options.get('company_name'):
            self.company_edit.setText(setup_options.get('company_name'))
            
        # Set license file
        if setup_options.get('license_file'):
            self.license_file_edit.setText(setup_options.get('license_file'))
            
        # Set desktop icon checkbox
        if 'desktop_icon' in setup_options:
            self.desktop_icon.setChecked(setup_options.get('desktop_icon'))
            
        # Set start menu checkbox
        if 'start_menu' in setup_options:
            self.start_menu.setChecked(setup_options.get('start_menu'))
            
        # Set default directory
        if setup_options.get('default_dir'):
            self.install_dir_edit.setText(setup_options.get('default_dir'))
            
    def getInstallerOptions(self):
        """Get the installer options from the dialog."""
        options = {
            "app_name": self.name_edit.text().strip(),
            "app_version": self.version_edit.text().strip(),
            "company_name": self.company_edit.text().strip(),
            "default_dir": self.install_dir_edit.text().strip(),
            "output_basename": self.output_name_edit.text().strip(),
            "compression": self.compression_combo.currentText(),
            "solid_compression": self.solid_compression.isChecked(),
            "icon_file": self.icon_file_edit.text().strip(),
            "license_file": self.license_file_edit.text().strip(),
            "create_desktop_icon": self.desktop_icon.isChecked(),
            "create_start_menu": self.start_menu.isChecked(),
            "run_after_install": self.run_after_install.isChecked(),
            "additional_files": self.additional_files
        }
        return options

class HelpDialog(QDialog):
    """Dialog to display help for the Enhanced PyInstaller GUI in a classical Windows help style."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced PyInstaller GUI Help")
        self.resize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create splitter for tree and content
        splitter = QSplitter(Qt.Horizontal)
        
        # Create tree widget for navigation
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(200)
        self.tree.currentItemChanged.connect(self.display_topic)
        
        # Create text browser for content
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        
        # Add widgets to splitter
        splitter.addWidget(self.tree)
        splitter.addWidget(self.content)
        splitter.setSizes([200, 600])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # Add help topics to the tree
        self.add_help_topics()
        
        # Select the first topic by default
        self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def add_help_topics(self):
        """Add help topics to the tree."""
        # Introduction
        intro = QTreeWidgetItem(self.tree, ["Introduction"])
        
        # General items under Introduction
        overview = QTreeWidgetItem(intro, ["Overview"])
        ui = QTreeWidgetItem(intro, ["User Interface"])
        
        # Features
        features = QTreeWidgetItem(self.tree, ["Features"])
        
        # Feature items
        files = QTreeWidgetItem(features, ["Adding Files"])
        packaging = QTreeWidgetItem(features, ["Packaging Scripts"])
        installers = QTreeWidgetItem(features, ["Creating Installers"])
        profiles = QTreeWidgetItem(features, ["Configuration Profiles"])
        batch = QTreeWidgetItem(features, ["Batch Conversion"])
        themes = QTreeWidgetItem(features, ["Themes"])
        drag_drop = QTreeWidgetItem(features, ["Drag & Drop"])
        
        # Expand all items
        self.tree.expandAll()
    
    def display_topic(self, current, previous):
        """Display the selected topic."""
        if not current:
            return
            
        topic_path = []
        item = current
        
        # Build the path to the selected item
        while item:
            topic_path.insert(0, item.text(0))
            item = item.parent()
            
        # Determine which content to show
        if len(topic_path) == 1 and topic_path[0] == "Introduction":
            self.show_introduction()
        elif len(topic_path) == 2 and topic_path[0] == "Introduction":
            if topic_path[1] == "Overview":
                self.show_overview()
            elif topic_path[1] == "User Interface":
                self.show_ui()
        elif len(topic_path) == 2 and topic_path[0] == "Features":
            if topic_path[1] == "Adding Files":
                self.show_adding_files()
            elif topic_path[1] == "Packaging Scripts":
                self.show_packaging()
            elif topic_path[1] == "Creating Installers":
                self.show_installers()
            elif topic_path[1] == "Configuration Profiles":
                self.show_profiles()
            elif topic_path[1] == "Batch Conversion":
                self.show_batch()
            elif topic_path[1] == "Themes":
                self.show_themes()
            elif topic_path[1] == "Drag & Drop":
                self.show_drag_drop()
    
    def show_introduction(self):
        """Show the introduction content."""
        content = """
        <h2>Introduction</h2>
        <p>Welcome to the Enhanced PyInstaller GUI!</p>
        
        <p>This application simplifies the process of converting Python scripts to standalone executables and creating installers for distribution.</p>
        
        <p>It provides a user-friendly interface to PyInstaller, a popular tool for packaging Python applications, eliminating the need to use command-line tools.</p>
        
        <p>Choose a topic from the navigation tree on the left to learn more about specific features and functionality.</p>
        """
        self.content.setHtml(content)
    
    def show_overview(self):
        """Show the overview content."""
        content = """
        <h2>Overview</h2>
        <p>The Enhanced PyInstaller GUI transforms command-line processes into a visual workflow.</p>
        
        <p><b>Key Benefits:</b></p>
        <ul>
            <li>No command-line knowledge required</li>
            <li>Visual feedback for conversion progress</li>
            <li>Ability to save configuration profiles for different projects</li>
            <li>Drag & drop support for adding files seamlessly</li>
            <li>Batch processing for converting multiple scripts at once</li>
            <li>Integrated installer creation with Inno Setup</li>
            <li>Modern user interface with multiple theme options</li>
        </ul>
        
        <p>Whether you're creating a simple utility or a complex application, this GUI helps streamline the entire process from development to distribution.</p>
        """
        self.content.setHtml(content)
    
    def show_ui(self):
        """Show the user interface content."""
        content = """
        <h2>User Interface</h2>
        <p>The Enhanced PyInstaller GUI features a modern, responsive user interface with the following components:</p>
        
        <ul>
            <li><b>File List:</b> Displays added Python scripts with drag & drop support</li>
            <li><b>Output Console:</b> Shows real-time conversion logs and application messages</li>
            <li><b>Progress Bar:</b> Visual indication of current operation progress</li>
            <li><b>Menu Bar:</b> Access to all application functions organized by category</li>
            <li><b>Toolbar:</b> Quick access to commonly used functions</li>
            <li><b>Status Bar:</b> Displays current application state and brief notifications</li>
        </ul>
        
        <p>The interface is designed to be intuitive for new users while providing efficiency for experienced users through keyboard shortcuts and streamlined workflows.</p>
        """
        self.content.setHtml(content)
    
    def show_adding_files(self):
        """Show the adding files content."""
        content = """
        <h2>Adding Files</h2>
        <p>There are multiple ways to add Python scripts to the file list for conversion.</p>
        
        <p><b>Methods:</b></p>
        <ul>
            <li><b>Add Files Button:</b> Click to open a file dialog and select one or more Python files</li>
            <li><b>Drag & Drop:</b> Drag files directly from File Explorer into the file list area</li>
            <li><b>File Menu:</b> Use the "Add Files" option in the File menu</li>
            <li><b>Keyboard Shortcut:</b> Press Ctrl+O to open the file dialog</li>
        </ul>
        
        <p><b>Supported File Types:</b></p>
        <ul>
            <li>Python scripts (.py)</li>
            <li>Python packages (directories containing __init__.py)</li>
        </ul>
        
        <p><b>File Management:</b></p>
        <ul>
            <li>Remove files by selecting them and clicking "Remove Selected" or pressing Delete</li>
            <li>Clear all files by clicking "Clear All" in the File menu</li>
            <li>Select multiple files using Ctrl+click or Shift+click</li>
        </ul>
        """
        self.content.setHtml(content)
    
    def show_packaging(self):
        """Show the packaging content."""
        content = """
        <h2>Packaging Scripts</h2>
        <p>Packaging converts your Python scripts into standalone executables that can run without a Python installation.</p>
        
        <p><b>Packaging Process:</b></p>
        <ol>
            <li>Add Python scripts to the file list</li>
            <li>Select a script to package</li>
            <li>Choose a configuration profile or create a new one</li>
            <li>Click "Package" in the toolbar or "Package Selected" in the File menu</li>
            <li>Monitor the conversion progress in the output console and progress bar</li>
        </ol>
        
        <p><b>Available Options:</b></p>
        <ul>
            <li><b>One-file/One-directory:</b> Create a single executable or a directory with dependencies</li>
            <li><b>Console/Windowed:</b> Show or hide the console window when the executable runs</li>
            <li><b>Icon:</b> Specify a custom icon for the executable</li>
            <li><b>Output Directory:</b> Choose where the executable will be saved</li>
            <li><b>Hidden Imports:</b> Add modules that PyInstaller cannot detect automatically</li>
            <li><b>Data Files:</b> Include additional files that your application needs</li>
            <li><b>Excluded Modules:</b> Specify modules to be excluded from the package</li>
            <li><b>UPX Compression:</b> Reduce the executable size (requires UPX)</li>
            <li><b>Debug Mode:</b> Include additional information for troubleshooting</li>
        </ul>
        
        <p><b>Output Location:</b></p>
        <p>By default, executables are saved in the "dist" directory in your project folder. You can specify a different location in the configuration profile.</p>
        """
        self.content.setHtml(content)
    
    def show_installers(self):
        """Show the installers content."""
        content = """
        <h2>Creating Installers</h2>
        <p>The Enhanced PyInstaller GUI integrates with Inno Setup to create professional installers for your applications.</p>
        
        <p><b>Prerequisites:</b></p>
        <ul>
            <li>Inno Setup Compiler must be installed and accessible in the system PATH</li>
            <li>A successful package (executable) must be created first</li>
        </ul>
        
        <p><b>Installer Creation Process:</b></p>
        <ol>
            <li>Select a script that has been successfully packaged</li>
            <li>Click "Create Installer" in the toolbar or File menu</li>
            <li>Configure installer options in the dialog that appears</li>
            <li>Click "Create" to generate the installer</li>
            <li>Monitor the creation process in the output console</li>
        </ol>
        
        <p><b>Installer Options:</b></p>
        <ul>
            <li><b>Application Name:</b> The name displayed in the installer and Programs list</li>
            <li><b>Version:</b> The application version number</li>
            <li><b>Company Name:</b> Your company or organization name</li>
            <li><b>Installation Directory:</b> Where the application will be installed</li>
            <li><b>Output Basename:</b> The filename for the installer executable</li>
            <li><b>License File:</b> Include a license agreement (optional)</li>
            <li><b>Icon File:</b> Custom icon for the installer (optional)</li>
            <li><b>Compression:</b> Level of compression for the installer</li>
            <li><b>Desktop Icon:</b> Create a shortcut on the desktop</li>
            <li><b>Start Menu:</b> Create entries in the Start menu</li>
        </ul>
        
        <p><b>Output Location:</b></p>
        <p>Installers are saved in the "build/Output" directory by default. The exact location is displayed upon successful creation.</p>
        """
        self.content.setHtml(content)
    
    def show_profiles(self):
        """Show the profiles content."""
        content = """
        <h2>Configuration Profiles</h2>
        <p>Configuration profiles allow you to save and reuse packaging settings for different projects or deployment scenarios.</p>
        
        <p><b>Profile Components:</b></p>
        <ul>
            <li><b>Basic Settings:</b> One-file/one-directory mode, console/windowed mode</li>
            <li><b>File Options:</b> Icon file, output directory, additional data and binary files</li>
            <li><b>Advanced Options:</b> Hidden imports, excluded modules, UPX compression, debug mode</li>
            <li><b>Installer Options:</b> Application metadata, installation preferences, installer appearance</li>
        </ul>
        
        <p><b>Profile Management Functions:</b></p>
        <ul>
            <li>Create new profiles with custom names</li>
            <li>Edit existing profiles to adjust settings</li>
            <li>Delete profiles that are no longer needed</li>
            <li>Set a default profile for new projects</li>
            <li>Export and import profiles to share with team members</li>
        </ul>
        
        <p><b>Profile Selection:</b></p>
        <p>Before packaging a script or creating an installer, you can select the profile to use. If no profile is selected, you'll be prompted to choose one or use the default profile.</p>
        """
        self.content.setHtml(content)
    
    def show_batch(self):
        """Show the batch conversion content."""
        content = """
        <h2>Batch Conversion</h2>
        <p>The batch conversion feature allows you to process multiple Python scripts in a single operation, saving time and effort.</p>
        
        <p><b>Key Capabilities:</b></p>
        <ul>
            <li>Convert multiple scripts sequentially with a single click</li>
            <li>Apply the same configuration profile to all selected scripts</li>
            <li>Monitor progress for the entire batch and individual scripts</li>
            <li>Cancel batch processing at any point</li>
            <li>Detailed logging for each script conversion</li>
            <li>Error handling that continues with remaining scripts if one fails</li>
        </ul>
        
        <p><b>How it Works:</b></p>
        <ol>
            <li>Add multiple Python scripts to the file list</li>
            <li>Select the scripts you want to include in the batch (use Ctrl+click or Shift+click)</li>
            <li>Click "Batch Convert" in the File menu</li>
            <li>Select a configuration profile to use for all scripts</li>
            <li>Monitor the progress as each script is processed</li>
        </ol>
        
        <p>For complex projects with multiple components, batch conversion can significantly reduce the time required to create deployable executables.</p>
        """
        self.content.setHtml(content)
    
    def show_themes(self):
        """Show the themes content."""
        content = """
        <h2>Themes</h2>
        <p>The Enhanced PyInstaller GUI offers multiple themes to customize the application appearance according to your preference.</p>
        
        <p><b>Available Themes:</b></p>
        <ul>
            <li><b>Light Theme:</b> Classic interface with high contrast and clean appearance</li>
            <li><b>Dark Theme:</b> Reduced eye strain for extended use with a modern aesthetic</li>
            <li><b>Matrix Theme:</b> Unique green-on-black styling for a distinctive look</li>
        </ul>
        
        <p><b>Changing Themes:</b></p>
        <ol>
            <li>Go to the Settings menu</li>
            <li>Select "Theme"</li>
            <li>Choose the desired theme from the submenu</li>
        </ol>
        
        <p><b>Theme Persistence:</b></p>
        <p>Your theme selection is saved and automatically applied when you restart the application.</p>
        """
        self.content.setHtml(content)
    
    def show_drag_drop(self):
        """Show the drag and drop content."""
        content = """
        <h2>Drag & Drop</h2>
        <p>The Enhanced PyInstaller GUI includes a sophisticated drag & drop system that allows you to directly add files from File Explorer or other applications.</p>
        
        <p><b>Supported Features:</b></p>
        <ul>
            <li>Drag single or multiple Python files directly into the file list</li>
            <li>Automatic file type validation to ensure only compatible files are added</li>
            <li>Visual feedback during drag operations</li>
            <li>Support for files from any location, including network drives</li>
        </ul>
        
        <p><b>Usage:</b></p>
        <ol>
            <li>Select one or more Python files in File Explorer</li>
            <li>Drag the selection over the file list area in the Enhanced PyInstaller GUI</li>
            <li>Release to add the files to the list</li>
        </ol>
        
        <p>The drag & drop functionality significantly speeds up your workflow by eliminating the need to navigate through file dialogs.</p>
        """
        self.content.setHtml(content)

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
        
        create_installer_action = QAction("Create Installer", self)
        create_installer_action.setShortcut("Ctrl+I")
        create_installer_action.triggered.connect(self.create_installer)
        file_menu.addAction(create_installer_action)
        
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
        
        # Remove Help Topics action and just keep About and Check for Updates
        # Help menu with complete documentation and support options
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Add Check for Updates action
        update_action = QAction("Check for Updates", self)
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)

        # Restore Help Topics action
        help_topics_action = QAction("Help Topics", self)
        help_topics_action.triggered.connect(self.show_help)
        help_topics_action.setShortcut(QKeySequence("F1"))
        help_menu.insertAction(about_action, help_topics_action)
        help_menu.insertSeparator(about_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Remove all toolbar actions
        # The toolbar will remain empty but can be filled 
        # with custom actions by users if needed
        
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
    
    def create_installer(self):
        """Create an installer for the selected Python script."""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a script to create an installer for.")
            return
        
        script_path = selected_items[0].text()
        
        # Use the current profile or select one
        if not self.current_profile:
            self.select_profile()
            if not self.current_profile:
                return
        
        # First, create an executable with PyInstaller
        self.log_message(f"Creating executable for {script_path} with profile {self.current_profile.name}")
        
        # Create a command based on the profile
        cmd = self.create_pyinstaller_command(script_path, self.current_profile.options)
        
        # Show the command in the output
        self.log_message(f"Command: {' '.join(cmd)}")
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Execute the command in a separate thread
        self.pyinstaller_thread = PyInstallerThread(cmd)
        self.pyinstaller_thread.progress_signal.connect(self.update_progress)
        self.pyinstaller_thread.message_signal.connect(self.log_message)
        self.pyinstaller_thread.finished.connect(lambda: self.on_exe_creation_finished(script_path))
        self.pyinstaller_thread.start()

    def on_exe_creation_finished(self, script_path):
        """Handle the completion of executable creation and proceed to create the installer."""
        self.log_message("Executable creation completed. Creating installer...")
        
        # Get the executable path
        exe_name = os.path.splitext(os.path.basename(script_path))[0] + ".exe"
        exe_path = os.path.abspath(os.path.join("dist", exe_name))
        
        # Log the path we're looking for
        self.log_message(f"Looking for executable at: {exe_path}")
        
        if not os.path.exists(exe_path):
            self.log_message(f"Error: Executable not found at {exe_path}")
            # Try alternative locations
            alt_paths = [
                os.path.join(os.getcwd(), "dist", exe_name),
                os.path.join(".", "dist", exe_name)
            ]
            for alt_path in alt_paths:
                self.log_message(f"Trying alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    exe_path = os.path.abspath(alt_path)
                    self.log_message(f"Found executable at: {exe_path}")
                    break
            else:
                self.log_message("Could not find executable in any expected location.")
                return
        
        # Get app name
        app_name = os.path.splitext(os.path.basename(script_path))[0]
        
        # Show installer options dialog
        dialog = InstallerOptionsDialog(app_name, self.current_profile, self)
        if not dialog.exec_():
            self.log_message("Installer creation cancelled by user.")
            return
        
        # Get installer options from dialog
        installer_options = dialog.getInstallerOptions()
        
        # Ensure the build directory exists
        os.makedirs("build", exist_ok=True)
        os.makedirs(os.path.join("build", "Output"), exist_ok=True)
        
        # Copy the executable to the build directory for Inno Setup
        build_exe_path = os.path.join("build", exe_name)
        try:
            import shutil
            self.log_message(f"Copying executable from {exe_path} to {build_exe_path}")
            shutil.copy2(exe_path, build_exe_path)
            
            # Create Inno Setup script using the executable in the build directory
            setup_script = self.create_inno_setup_script(script_path, build_exe_path, installer_options)
            script_path = os.path.join("build", "setup.iss")
            
            # Write the script to a file
            with open(script_path, 'w') as f:
                f.write(setup_script)
            
            self.log_message(f"Created Inno Setup script at {script_path}")
            
            # Find Inno Setup compiler
            iscc_path = self.find_inno_setup_compiler()
            if not iscc_path:
                self.log_message("Error: Inno Setup compiler not found. Please install Inno Setup.")
                return
            
            # Compile the script
            self.log_message("Compiling installer...")
            compile_cmd = [iscc_path, script_path]
            
            # Run in a new thread
            self.inno_thread = QThread()
            self.inno_worker = InnoSetupWorker(compile_cmd)
            self.inno_worker.moveToThread(self.inno_thread)
            self.inno_thread.started.connect(self.inno_worker.run)
            self.inno_worker.progress_signal.connect(self.update_progress)
            self.inno_worker.message_signal.connect(self.log_message)
            self.inno_worker.finished_signal.connect(self.on_installer_creation_finished)
            self.inno_worker.finished_signal.connect(self.inno_thread.quit)
            self.inno_thread.start()
            
        except Exception as e:
            self.log_message(f"Error creating installer: {str(e)}")
    
    def find_inno_setup_compiler(self):
        """Find the Inno Setup compiler (iscc.exe) on the system."""
        # Common installation locations
        possible_paths = [
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        import subprocess
        try:
            result = subprocess.run(["where", "iscc"], capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None

    def create_inno_setup_script(self, script_path, exe_path, installer_options):
        """Create an Inno Setup script for the executable."""
        # Get the safe app name (no special characters)
        app_name = os.path.splitext(os.path.basename(script_path))[0]
        safe_app_name = re.sub(r'[^\w]', '_', app_name)
        
        # Get values from installer options
        app_name = installer_options.get('app_name', app_name)
        app_version = installer_options.get('app_version', '1.0.0')
        app_publisher = installer_options.get('company_name', 'Your Company')
        output_dir = installer_options.get('output_dir', 'installer')
        output_basename = installer_options.get('output_basename', f"{app_name}_setup")
        license_file = installer_options.get('license_file', '')
        icon_file = installer_options.get('icon_file', '')
        default_dir = installer_options.get('default_dir', '{pf}\\{#MyAppName}')
        create_desktop_icon = installer_options.get('create_desktop_icon', True)
        create_start_menu = installer_options.get('create_start_menu', True)
        compression = installer_options.get('compression', 'lzma')
        
        # Extract just the executable name
        exe_name = os.path.basename(exe_path)
        
        # Log the executable information
        app_logger.info(f"Using executable name: {exe_name}")
        
        # Create the script content
        script = f"""#define MyAppName "{app_name}"
#define MyAppVersion "{app_version}"
#define MyAppPublisher "{app_publisher}"
#define MyAppExeName "{exe_name}"

[Setup]
AppId={{{{{safe_app_name}}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={default_dir}
DefaultGroupName={{#MyAppName}}
OutputDir=build\\Output
OutputBaseFilename={output_basename}
Compression={compression}
SolidCompression=yes
"""
        # Note: PrivilegesRequired removed for Linux version (Windows/Inno Setup specific)

        # Add license file if provided
        if license_file and os.path.exists(license_file):
            script += f"LicenseFile={license_file}\n"
            
        # Add icon file if provided
        if icon_file and os.path.exists(icon_file):
            script += f"SetupIconFile={icon_file}\n"

        script += """
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
"""
        # Use the simple filename without path since it's in the same directory as the script
        script += f'Source: "{exe_name}"; DestDir: "{{app}}"; Flags: ignoreversion\n'

        # Add additional files from installer options
        additional_files = installer_options.get('additional_files', [])
        critical_files = []  # Track critical files for validation
        
        for file_info in additional_files:
            file_path = file_info['path']
            is_critical = file_info['critical']
            file_type = file_info['type']
            
            if not os.path.exists(file_path):
                app_logger.warning(f"Additional file not found: {file_path}")
                continue
            
            # Get relative or absolute path for the source
            # Copy file to build directory so Inno Setup can find it
            file_basename = os.path.basename(file_path)
            
            if file_type == 'folder':
                # For folders, include all contents recursively
                folder_name = os.path.basename(file_path.rstrip('\\/'))
                script += f'Source: "{file_path}\\*"; DestDir: "{{app}}\\{folder_name}"; Flags: ignoreversion recursesubdirs createallsubdirs'
                
                if is_critical:
                    critical_files.append(folder_name)
                    script += f'; Check: CheckCriticalFolder("{folder_name}")'
                
                script += '\n'
            else:
                # For individual files
                script += f'Source: "{file_path}"; DestDir: "{{app}}"; Flags: ignoreversion'
                
                if is_critical:
                    critical_files.append(file_basename)
                    script += f'; Check: CheckCriticalFile("{file_basename}")'
                
                script += '\n'

        script += """
[Icons]
"""
        
        # Add desktop icon if requested
        if create_desktop_icon:
            script += """Name: "{commondesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon\n"""
            
        # Add start menu entries if requested
        if create_start_menu:
            script += """Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"\n"""
            script += """Name: "{group}\\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"\n"""

        script += """
[Tasks]
"""
        
        # Add desktop icon task if requested
        if create_desktop_icon:
            script += """Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked\n"""

        script += """
[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"""

        # Add [Code] section for critical file checking if there are critical files
        if critical_files:
            script += """
[Code]
function CheckCriticalFile(FileName: String): Boolean;
var
  FilePath: String;
begin
  FilePath := ExpandConstant('{src}\\') + FileName;
  Result := FileExists(FilePath);
  if not Result then
  begin
    MsgBox('Critical file not found: ' + FileName + #13#10 + 
           'The installation cannot continue without this file.', 
           mbError, MB_OK);
  end;
end;

function CheckCriticalFolder(FolderName: String): Boolean;
var
  FolderPath: String;
begin
  FolderPath := ExpandConstant('{src}\\') + FolderName;
  Result := DirExists(FolderPath);
  if not Result then
  begin
    MsgBox('Critical folder not found: ' + FolderName + #13#10 + 
           'The installation cannot continue without this folder.', 
           mbError, MB_OK);
  end;
end;
"""

        return script

    def on_installer_creation_finished(self, success, message):
        """Handle the completion of installer creation."""
        if success:
            self.log_message("Installer creation completed successfully!")
            self.progress_bar.setValue(100)
            
            # Show a message box with the output location
            output_dir = os.path.abspath(os.path.join("build", "Output"))
            QMessageBox.information(
                self, 
                "Installer Created", 
                f"The installer has been created successfully!\nLocation: {output_dir}"
            )
        else:
            self.log_message(f"Installer creation failed: {message}")
    
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
        QMessageBox.about(
            self,
            "About Enhanced PyInstaller GUI",
            """
            <h2>Enhanced PyInstaller GUI</h2>
            <p>A modern graphical interface for PyInstaller</p>
            <p>Version 1.0.0</p>
            <p>© 2023</p>
            <p>This application simplifies the process of converting Python scripts to standalone executables.</p>
            <p>Features:</p>
            <ul>
                <li>Modern user interface with dark mode support</li>
                <li>Drag and drop support for Python files</li>
                <li>Configuration profiles for reusing settings</li>
                <li>Integrated installer creation with Inno Setup</li>
                <li>Batch conversion for multiple files</li>
                <li>Automatic updates</li>
            </ul>
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

    def show_help(self):
        """Show the help dialog."""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

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
        app = QApplication(sys.argv)
        main_window = EnhancedPyInstallerGUI()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        app_logger.error(f"Application error: {e}")
        print(f"Application error: {e}")
        sys.exit(1)