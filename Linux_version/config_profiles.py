"""
Configuration profiles for Enhanced PyInstaller GUI
Provides classes for managing PyInstaller configuration profiles
"""

import os
import json
import copy
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, 
    QLabel, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox,
    QMessageBox, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QSettings

class ConfigProfile:
    """Configuration profile for PyInstaller settings."""
    
    def __init__(self, name, options=None):
        """
        Initialize a configuration profile.
        
        Args:
            name: Profile name
            options: Dictionary of PyInstaller options
        """
        self.name = name
        self.options = options or {}
    
    def to_dict(self):
        """
        Convert profile to dictionary for serialization.
        
        Returns:
            dict: Profile as a dictionary
        """
        return {
            'name': self.name,
            'options': self.options
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a profile from a dictionary.
        
        Args:
            data: Dictionary with profile data
            
        Returns:
            ConfigProfile: New profile instance
        """
        return cls(data.get('name', 'Unnamed'), data.get('options', {}))

class ProfileManager:
    """Manages configuration profiles for PyInstaller settings."""
    
    def __init__(self):
        """Initialize the profile manager."""
        self.settings = QSettings("EnhancedPyInstallerGUI", "Profiles")
        self.load_profiles()
    
    def load_profiles(self):
        """Load profiles from settings."""
        self.profiles = {}
        
        # Get profile names
        size = self.settings.beginReadArray("profiles")
        for i in range(size):
            self.settings.setArrayIndex(i)
            name = self.settings.value("name")
            options_json = self.settings.value("options", "{}")
            
            try:
                options = json.loads(options_json)
            except json.JSONDecodeError:
                options = {}
            
            self.profiles[name] = ConfigProfile(name, options)
        
        self.settings.endArray()
        
        # If no profiles exist, create a default one
        if not self.profiles:
            self._create_default_profile()
    
    def save_profiles(self):
        """Save profiles to settings."""
        self.settings.beginWriteArray("profiles")
        
        for i, (name, profile) in enumerate(self.profiles.items()):
            self.settings.setArrayIndex(i)
            self.settings.setValue("name", name)
            self.settings.setValue("options", json.dumps(profile.options))
        
        self.settings.endArray()
        self.settings.sync()
    
    def _create_default_profile(self):
        """Create a default profile with basic settings."""
        default_profile = ConfigProfile(
            "Default",
            {
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
        
        self.profiles["Default"] = default_profile
        self.set_default_profile("Default")
        self.save_profiles()
    
    def add_profile(self, profile):
        """
        Add a profile to the manager.
        
        Args:
            profile: ConfigProfile instance
        """
        self.profiles[profile.name] = profile
        self.save_profiles()
    
    def update_profile(self, name, options):
        """
        Update a profile's options.
        
        Args:
            name: Profile name
            options: New options dictionary
        """
        if name in self.profiles:
            self.profiles[name].options = options
            self.save_profiles()
    
    def remove_profile(self, name):
        """
        Remove a profile from the manager.
        
        Args:
            name: Profile name
        """
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
    
    def get_profile(self, name):
        """
        Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            ConfigProfile: Profile instance or None if not found
        """
        return self.profiles.get(name)
    
    def get_all_profiles(self):
        """
        Get all profiles.
        
        Returns:
            dict: Dictionary of profile name to profile instance
        """
        return self.profiles
    
    def get_default_profile(self):
        """
        Get the default profile.
        
        Returns:
            ConfigProfile: Default profile instance or None if not set
        """
        default_name = self.settings.value("default_profile")
        if default_name and default_name in self.profiles:
            return self.profiles[default_name]
        
        # If no default is set or the default doesn't exist anymore, use the first profile
        if self.profiles:
            first_profile = next(iter(self.profiles.values()))
            self.set_default_profile(first_profile.name)
            return first_profile
        
        return None
    
    def set_default_profile(self, name):
        """
        Set the default profile.
        
        Args:
            name: Profile name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name in self.profiles:
            self.settings.setValue("default_profile", name)
            self.settings.sync()
            return True
        return False

class ProfileSelectionDialog(QDialog):
    """Dialog for selecting a configuration profile."""
    
    def __init__(self, profile_manager, parent=None):
        """
        Initialize the profile selection dialog.
        
        Args:
            profile_manager: ProfileManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.selected_profile = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Select Profile")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select a configuration profile to use:")
        layout.addWidget(instructions)
        
        # Profile list
        self.profile_list = QListWidget()
        self.populate_profiles()
        layout.addWidget(self.profile_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.accept)
        
        manage_button = QPushButton("Manage Profiles")
        manage_button.clicked.connect(self.manage_profiles)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(manage_button)
        button_layout.addStretch()
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_profiles(self):
        """Populate the profile list."""
        self.profile_list.clear()
        
        profiles = self.profile_manager.get_all_profiles()
        default_profile = self.profile_manager.get_default_profile()
        
        for name, profile in profiles.items():
            item_text = name
            if default_profile and name == default_profile.name:
                item_text += " (Default)"
            
            self.profile_list.addItem(item_text)
            
            # Select the default profile by default
            if default_profile and name == default_profile.name:
                self.profile_list.setCurrentRow(self.profile_list.count() - 1)
    
    def manage_profiles(self):
        """Open the profile management dialog."""
        dialog = ProfileManagementDialog(self.profile_manager, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Refresh the profile list
            self.populate_profiles()
    
    def accept(self):
        """Handle the accept action."""
        if not self.profile_list.currentItem():
            QMessageBox.warning(self, "No Selection", "Please select a profile")
            return
        
        # Extract the profile name (remove " (Default)" if present)
        item_text = self.profile_list.currentItem().text()
        if " (Default)" in item_text:
            profile_name = item_text.replace(" (Default)", "")
        else:
            profile_name = item_text
        
        self.selected_profile = self.profile_manager.get_profile(profile_name)
        
        if not self.selected_profile:
            QMessageBox.warning(self, "Error", f"Profile '{profile_name}' not found")
            return
        
        super().accept()

class ProfileManagementDialog(QDialog):
    """Dialog for managing configuration profiles."""
    
    def __init__(self, profile_manager, parent=None):
        """
        Initialize the profile management dialog.
        
        Args:
            profile_manager: ProfileManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Manage Profiles")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Profile list and buttons
        list_layout = QHBoxLayout()
        
        # Profile list
        self.profile_list = QListWidget()
        self.populate_profiles()
        list_layout.addWidget(self.profile_list)
        
        # Buttons for profile management
        button_layout = QVBoxLayout()
        
        new_button = QPushButton("New")
        new_button.clicked.connect(self.new_profile)
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_profile)
        
        duplicate_button = QPushButton("Duplicate")
        duplicate_button.clicked.connect(self.duplicate_profile)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_profile)
        
        set_default_button = QPushButton("Set as Default")
        set_default_button.clicked.connect(self.set_default_profile)
        
        button_layout.addWidget(new_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(duplicate_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(set_default_button)
        button_layout.addStretch()
        
        list_layout.addLayout(button_layout)
        
        layout.addLayout(list_layout)
        
        # Dialog buttons
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        
        layout.addWidget(dialog_buttons)
    
    def populate_profiles(self):
        """Populate the profile list."""
        self.profile_list.clear()
        
        profiles = self.profile_manager.get_all_profiles()
        default_profile = self.profile_manager.get_default_profile()
        
        for name, profile in profiles.items():
            item_text = name
            if default_profile and name == default_profile.name:
                item_text += " (Default)"
            
            self.profile_list.addItem(item_text)
    
    def get_selected_profile_name(self):
        """
        Get the name of the selected profile.
        
        Returns:
            str: Profile name or None if no profile is selected
        """
        if not self.profile_list.currentItem():
            return None
        
        item_text = self.profile_list.currentItem().text()
        if " (Default)" in item_text:
            return item_text.replace(" (Default)", "")
        
        return item_text
    
    def new_profile(self):
        """Create a new profile."""
        dialog = ProfileEditDialog(None, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted and dialog.profile:
            # Check if profile name already exists
            if dialog.profile.name in self.profile_manager.get_all_profiles():
                QMessageBox.warning(self, "Duplicate Name", f"Profile '{dialog.profile.name}' already exists")
                return
            
            self.profile_manager.add_profile(dialog.profile)
            self.populate_profiles()
    
    def edit_profile(self):
        """Edit the selected profile."""
        profile_name = self.get_selected_profile_name()
        if not profile_name:
            QMessageBox.warning(self, "No Selection", "Please select a profile to edit")
            return
        
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", f"Profile '{profile_name}' not found")
            return
        
        dialog = ProfileEditDialog(profile, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted and dialog.profile:
            # Update the profile
            self.profile_manager.update_profile(profile_name, dialog.profile.options)
            
            # Rename if needed
            if dialog.profile.name != profile_name:
                # Check if new name already exists
                if dialog.profile.name in self.profile_manager.get_all_profiles():
                    QMessageBox.warning(self, "Duplicate Name", f"Profile '{dialog.profile.name}' already exists")
                    return
                
                # Remove old profile and add new one with updated name
                self.profile_manager.remove_profile(profile_name)
                self.profile_manager.add_profile(dialog.profile)
            
            self.populate_profiles()
    
    def duplicate_profile(self):
        """Duplicate the selected profile."""
        profile_name = self.get_selected_profile_name()
        if not profile_name:
            QMessageBox.warning(self, "No Selection", "Please select a profile to duplicate")
            return
        
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", f"Profile '{profile_name}' not found")
            return
        
        # Create a copy with a new name
        new_name = f"{profile_name} Copy"
        counter = 1
        
        # Find a unique name
        while new_name in self.profile_manager.get_all_profiles():
            counter += 1
            new_name = f"{profile_name} Copy {counter}"
        
        # Create the duplicate profile
        duplicate_profile = ConfigProfile(new_name, copy.deepcopy(profile.options))
        self.profile_manager.add_profile(duplicate_profile)
        
        self.populate_profiles()
    
    def delete_profile(self):
        """Delete the selected profile."""
        profile_name = self.get_selected_profile_name()
        if not profile_name:
            QMessageBox.warning(self, "No Selection", "Please select a profile to delete")
            return
        
        # Don't allow deleting the last profile
        if len(self.profile_manager.get_all_profiles()) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the last remaining profile")
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self.profile_manager.remove_profile(profile_name)
            self.populate_profiles()
    
    def set_default_profile(self):
        """Set the selected profile as the default."""
        profile_name = self.get_selected_profile_name()
        if not profile_name:
            QMessageBox.warning(self, "No Selection", "Please select a profile to set as default")
            return
        
        self.profile_manager.set_default_profile(profile_name)
        self.populate_profiles()

class ProfileEditDialog(QDialog):
    """Dialog for editing a configuration profile."""
    
    def __init__(self, profile, parent=None):
        """
        Initialize the profile edit dialog.
        
        Args:
            profile: ConfigProfile instance or None for a new profile
            parent: Parent widget
        """
        super().__init__(parent)
        self.original_profile = profile
        self.profile = None
        self.setup_ui()
        
        # If editing an existing profile, load its values
        if self.original_profile:
            self.load_profile(self.original_profile)
    
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Edit Profile" if self.original_profile else "New Profile")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Profile name
        name_layout = QHBoxLayout()
        name_label = QLabel("Profile Name:")
        self.name_edit = QLineEdit()
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # Basic options
        basic_group_layout = QFormLayout()
        
        # Packaging type
        self.onefile_checkbox = QCheckBox("One-file mode (single executable)")
        self.onefile_checkbox.setChecked(True)
        basic_group_layout.addRow("", self.onefile_checkbox)
        
        # Console mode
        self.console_checkbox = QCheckBox("Console mode (show terminal)")
        basic_group_layout.addRow("", self.console_checkbox)
        
        # Icon selection
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        browse_icon_button = QPushButton("Browse...")
        browse_icon_button.clicked.connect(self.browse_icon)
        
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(browse_icon_button)
        
        basic_group_layout.addRow("Icon:", icon_layout)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setText("dist")
        browse_output_button = QPushButton("Browse...")
        browse_output_button.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(browse_output_button)
        
        basic_group_layout.addRow("Output Directory:", output_layout)
        
        layout.addLayout(basic_group_layout)
        
        # Advanced options
        advanced_group_layout = QFormLayout()
        
        # Clean build
        self.clean_build_checkbox = QCheckBox("Clean build (remove previous build files)")
        self.clean_build_checkbox.setChecked(True)
        advanced_group_layout.addRow("", self.clean_build_checkbox)
        
        # UPX compression
        self.upx_compress_checkbox = QCheckBox("Use UPX compression (if installed)")
        advanced_group_layout.addRow("", self.upx_compress_checkbox)
        
        # Debug mode
        self.debug_checkbox = QCheckBox("Debug mode (include debugging information)")
        advanced_group_layout.addRow("", self.debug_checkbox)
        
        # Note: Administrator privileges option removed for Linux version
        # Linux users should use sudo if root access is needed
        
        layout.addLayout(advanced_group_layout)
        
        # Hidden imports
        self.hidden_imports_edit = QLineEdit()
        self.hidden_imports_edit.setPlaceholderText("module1,module2,module3")
        layout.addWidget(QLabel("Hidden Imports (comma-separated):"))
        layout.addWidget(self.hidden_imports_edit)
        
        # Excluded modules
        self.exclude_modules_edit = QLineEdit()
        self.exclude_modules_edit.setPlaceholderText("module1,module2,module3")
        layout.addWidget(QLabel("Excluded Modules (comma-separated):"))
        layout.addWidget(self.exclude_modules_edit)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_profile)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def load_profile(self, profile):
        """
        Load profile values into the UI.
        
        Args:
            profile: ConfigProfile instance
        """
        self.name_edit.setText(profile.name)
        
        options = profile.options
        self.onefile_checkbox.setChecked(options.get("onefile", True))
        self.console_checkbox.setChecked(options.get("console_mode", False))
        self.icon_edit.setText(options.get("icon_path", ""))
        self.output_edit.setText(options.get("output_dir", "dist"))
        self.clean_build_checkbox.setChecked(options.get("clean_build", True))
        self.upx_compress_checkbox.setChecked(options.get("upx_compress", False))
        self.debug_checkbox.setChecked(options.get("debug", False))
        # Note: require_admin removed for Linux version
        
        # Load hidden imports
        hidden_imports = options.get("hidden_imports", [])
        self.hidden_imports_edit.setText(",".join(hidden_imports))
        
        # Load excluded modules
        exclude_modules = options.get("exclude_modules", [])
        self.exclude_modules_edit.setText(",".join(exclude_modules))
    
    def save_profile(self):
        """Save the profile from UI values."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a profile name")
            return
        
        # Parse hidden imports
        hidden_imports_text = self.hidden_imports_edit.text().strip()
        if hidden_imports_text:
            hidden_imports = [imp.strip() for imp in hidden_imports_text.split(",")]
        else:
            hidden_imports = []
        
        # Parse excluded modules
        exclude_modules_text = self.exclude_modules_edit.text().strip()
        if exclude_modules_text:
            exclude_modules = [mod.strip() for mod in exclude_modules_text.split(",")]
        else:
            exclude_modules = []
        
        # Create options dictionary
        options = {
            "onefile": self.onefile_checkbox.isChecked(),
            "console_mode": self.console_checkbox.isChecked(),
            "icon_path": self.icon_edit.text(),
            "output_dir": self.output_edit.text(),
            "clean_build": self.clean_build_checkbox.isChecked(),
            "upx_compress": self.upx_compress_checkbox.isChecked(),
            "debug": self.debug_checkbox.isChecked(),
            # Note: require_admin removed for Linux version
            "hidden_imports": hidden_imports,
            "data_files": [],  # Not editable in this dialog
            "binary_files": [],  # Not editable in this dialog
            "exclude_modules": exclude_modules
        }
        
        # Create or update the profile
        self.profile = ConfigProfile(name, options)
        self.accept()
    
    def browse_icon(self):
        """Browse for an icon file."""
        file_dialog = QFileDialog()
        icon_path, _ = file_dialog.getOpenFileName(
            self, "Select Icon File", "", "Icon Files (*.ico *.icns *.png);;All Files (*.*)"
        )
        
        if icon_path:
            self.icon_edit.setText(icon_path)
    
    def browse_output(self):
        """Browse for an output directory."""
        file_dialog = QFileDialog()
        output_dir = file_dialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        
        if output_dir:
            self.output_edit.setText(output_dir)