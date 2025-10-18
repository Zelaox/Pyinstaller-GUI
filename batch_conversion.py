"""
Batch conversion functionality for Enhanced PyInstaller GUI
Provides classes for managing batch processing of multiple files
"""

import os
import json
import subprocess
import threading
import logging
from typing import List, Dict, Any, Callable
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QSettings

logger = logging.getLogger(__name__)

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

class BatchConversionManager(QObject):
    """Manages batch conversion of multiple Python scripts."""
    
    # Signals for progress updates
    batch_progress_signal = pyqtSignal(int)
    script_progress_signal = pyqtSignal(int)
    script_status_signal = pyqtSignal(str, str)
    batch_completed_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize the batch conversion manager.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.conversion_running = False
        self.cancel_requested = False
    
    def start_batch_conversion(self, scripts, profile):
        """
        Start batch conversion of multiple scripts.
        
        Args:
            scripts: List of script paths
            profile: Configuration profile to use
        """
        if self.conversion_running:
            return
        
        self.conversion_running = True
        self.cancel_requested = False
        
        # Start conversion in a separate thread
        threading.Thread(
            target=self._convert_batch,
            args=(scripts, profile),
            daemon=True
        ).start()
    
    def _convert_batch(self, scripts, profile):
        """
        Convert a batch of scripts in a separate thread.
        
        Args:
            scripts: List of script paths
            profile: Configuration profile to use
        """
        total_scripts = len(scripts)
        completed_scripts = 0
        
        for script_path in scripts:
            if self.cancel_requested:
                self.script_status_signal.emit(script_path, "Cancelled")
                break
            
            self.script_status_signal.emit(script_path, "In progress")
            
            # Create PyInstaller command
            cmd = self._create_pyinstaller_command(script_path, profile.options)
            
            # Execute command
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                
                # Phases with progress
                phases = [
                    (20, "Analyzing imports..."),
                    (40, "Collecting modules..."),
                    (60, "Building EXE..."),
                    (80, "Finalizing package...")
                ]
                
                for progress, message in phases:
                    if self.cancel_requested or process.poll() is not None:
                        break
                    
                    self.script_progress_signal.emit(progress)
                    
                    # Wait before checking next phase
                    for _ in range(5):
                        if self.cancel_requested or process.poll() is not None:
                            break
                        import time
                        time.sleep(0.5)
                
                # Wait for process to complete
                stdout, stderr = process.communicate()
                
                # Check result
                if process.returncode == 0:
                    self.script_progress_signal.emit(100)
                    self.script_status_signal.emit(script_path, "Completed")
                else:
                    logger.error(f"Error converting {script_path}: {stderr}")
                    self.script_progress_signal.emit(0)
                    self.script_status_signal.emit(script_path, "Failed")
                    
            except Exception as e:
                logger.error(f"Error during conversion: {e}")
                self.script_progress_signal.emit(0)
                self.script_status_signal.emit(script_path, f"Error: {str(e)}")
            
            completed_scripts += 1
            batch_progress = int((completed_scripts / total_scripts) * 100)
            self.batch_progress_signal.emit(batch_progress)
        
        self.conversion_running = False
        self.batch_completed_signal.emit()
    
    def _create_pyinstaller_command(self, script_path, options):
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
        
        # Add debug option
        if options.get("debug", False):
            cmd.extend(["-d", "all"])
        
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
    
    def cancel_conversion(self):
        """Cancel the current batch conversion."""
        self.cancel_requested = True
