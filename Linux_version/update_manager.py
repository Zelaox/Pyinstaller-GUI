"""
Update Manager for Enhanced PyInstaller GUI

This module handles checking for updates and applying them to the application.
It uses a predefined URL to fetch the latest version information and compares
it with the locally stored version.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse
import ssl
import shutil
import tempfile
import sys
import subprocess
import time

logger = logging.getLogger(__name__)

# URL to check for updates
# In a real application, this would be a URL to a JSON file on a server
# For GitHub releases, you could use the API endpoint for releases
UPDATE_CHECK_URL = "https://api.github.com/repos/your-username/enhanced-pyinstaller-gui/releases/latest"

# Version information file path
VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.json")

def get_current_version():
    """
    Get the current version of the application from the version.json file
    
    Returns:
        dict: The version information or None if the file doesn't exist
    """
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                version_info = json.load(f)
            return version_info
        
        # If version file doesn't exist, create one with default values
        default_version = {
            "version": "1.0.0",
            "build_date": time.strftime("%Y-%m-%d"),
            "channel": "stable"
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
        
        # Write default version file
        with open(VERSION_FILE, 'w') as f:
            json.dump(default_version, f, indent=4)
            
        logger.info(f"Created default version file at {VERSION_FILE}")
        return default_version
    except Exception as e:
        logger.error(f"Failed to read current version: {e}")
        return None

def parse_version(version_str):
    """
    Parse a version string into a tuple of integers for comparison
    
    Args:
        version_str (str): The version string in format "x.y.z"
        
    Returns:
        tuple: A tuple of integers representing the version
    """
    try:
        return tuple(map(int, version_str.split('.')))
    except Exception:
        return (0, 0, 0)  # Default for invalid version strings

def check_for_updates(parent=None):
    """
    Check if updates are available by comparing the local version with remote
    
    Args:
        parent: Optional parent window for displaying dialogs
    
    Returns:
        bool: True if an update was applied, False otherwise
    """
    current_version = get_current_version()
    if not current_version:
        if parent:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Update Check Failed", "Could not determine current version")
        return False
    
    try:
        # Create a context that doesn't verify certificates for testing
        # In production, remove this and use proper certificate verification
        context = ssl._create_unverified_context()
        
        # Set headers for GitHub API
        headers = {
            'User-Agent': 'EnhancedPyInstallerGUI/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Create request with headers
        req = urllib.request.Request(UPDATE_CHECK_URL, headers=headers)
        
        # Fetch the latest version information
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            if response.status != 200:
                if parent:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(parent, "Update Check Failed", f"Update check failed with status code: {response.status}")
                return False
            
            github_release = json.loads(response.read().decode('utf-8'))
            
            # Extract version from GitHub tag name (e.g. "v1.0.0" -> "1.0.0")
            version_str = github_release.get('tag_name', '0.0.0')
            if version_str.startswith('v'):
                version_str = version_str[1:]
                
            # Create a version info dictionary from GitHub release data
            latest_version_info = {
                "version": version_str,
                "details": github_release.get('body', 'No release notes provided'),
                "published_at": github_release.get('published_at', '')
            }
            
            # Find the asset to download (first .zip or .exe file)
            assets = github_release.get('assets', [])
            for asset in assets:
                download_url = asset.get('browser_download_url', '')
                if download_url.endswith('.zip') or download_url.endswith('.exe'):
                    latest_version_info['download_url'] = download_url
                    break
            
            # Compare versions
            current_version_tuple = parse_version(current_version.get("version", "0.0.0"))
            latest_version_tuple = parse_version(latest_version_info.get("version", "0.0.0"))
            
            update_available = latest_version_tuple > current_version_tuple
            
            if not update_available:
                if parent:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(parent, "No Updates Available", "You are currently running the latest version.")
                return False
                
            # If an update is available and we have a parent window, ask the user if they want to update
            if parent:
                from PyQt5.QtWidgets import QMessageBox
                version = latest_version_info.get("version", "Unknown")
                details = latest_version_info.get("details", "No details provided")
                
                message = f"A new version ({version}) is available!\n\nChanges:\n{details}\n\nWould you like to download and install this update now?"
                response = QMessageBox.question(parent, "Update Available", message, 
                                              QMessageBox.Yes | QMessageBox.No)
                
                if response == QMessageBox.Yes:
                    # Download and apply the update
                    download_url = latest_version_info.get("download_url")
                    if download_url:
                        if parent:
                            parent.log_message(f"Downloading update from {download_url}...")
                        
                        success, file_path, error = download_update(download_url)
                        
                        if success:
                            parent.log_message("Download completed. Applying update...")
                            apply_success, apply_error = apply_update(file_path)
                            
                            if apply_success:
                                return True
                            else:
                                if parent:
                                    QMessageBox.critical(parent, "Update Failed", f"Failed to apply update: {apply_error}")
                                return False
                        else:
                            if parent:
                                QMessageBox.critical(parent, "Download Failed", f"Failed to download update: {error}")
                            return False
                    else:
                        if parent:
                            QMessageBox.warning(parent, "Update Error", "No download URL provided for the update")
                        return False
            
            return False
            
    except urllib.error.URLError as e:
        if parent:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Connection Error", f"Failed to connect to update server: {e}")
        return False
    except json.JSONDecodeError:
        if parent:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Update Error", "Invalid version information received")
        return False
    except Exception as e:
        if parent:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Update Error", f"Error checking for updates: {e}")
        return False

def download_update(download_url, save_path=None):
    """
    Download the update package from the specified URL
    
    Args:
        download_url (str): URL of the update package
        save_path (str, optional): Path to save the downloaded file
        
    Returns:
        tuple: (success, file_path, error_message)
            - success (bool): True if download was successful
            - file_path (str): Path to the downloaded file or None
            - error_message (str): Error message if any, None otherwise
    """
    if not save_path:
        # Create a temporary file with the correct extension
        parsed_url = urlparse(download_url)
        file_name = os.path.basename(parsed_url.path)
        extension = os.path.splitext(file_name)[1]
        
        fd, temp_path = tempfile.mkstemp(suffix=extension)
        os.close(fd)
        save_path = temp_path
    
    try:
        # Create a context that doesn't verify certificates for testing
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(download_url, context=context, timeout=30) as response:
            if response.status != 200:
                return False, None, f"Download failed with status code: {response.status}"
            
            with open(save_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
                
        return True, save_path, None
    
    except Exception as e:
        return False, None, f"Error downloading update: {e}"

def apply_update(update_file_path):
    """
    Apply the downloaded update
    
    Args:
        update_file_path (str): Path to the downloaded update file
        
    Returns:
        tuple: (success, error_message)
            - success (bool): True if update was successfully applied
            - error_message (str): Error message if any, None otherwise
    """
    if not os.path.exists(update_file_path):
        return False, "Update file not found"
    
    # Determine file type by extension
    file_ext = os.path.splitext(update_file_path)[1].lower()
    
    try:
        if file_ext == '.exe':
            # For executable installers, run them
            subprocess.Popen([update_file_path], shell=True)
            return True, None
            
        elif file_ext == '.zip':
            # For zip files, extract them to the application directory
            import zipfile
            app_dir = os.path.dirname(os.path.abspath(__file__))
            
            with zipfile.ZipFile(update_file_path, 'r') as zip_ref:
                # Create a backup of current files
                backup_dir = os.path.join(tempfile.gettempdir(), f"pyinstaller_gui_backup_{int(time.time())}")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Copy current files to backup
                for item in os.listdir(app_dir):
                    s = os.path.join(app_dir, item)
                    d = os.path.join(backup_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                
                # Extract new files
                zip_ref.extractall(app_dir)
                
            return True, None
        else:
            return False, f"Unsupported update file type: {file_ext}"
            
    except Exception as e:
        return False, f"Error applying update: {e}"

if __name__ == "__main__":
    # Testing the update functionality
    print("Checking for updates...")
    update_applied = check_for_updates()
    
    if not update_applied:
        print("No updates were applied.")
        
        # For testing, we can manually test the download and apply functions
        current_version = get_current_version()
        if current_version:
            print(f"Current version: {current_version.get('version', 'Unknown')}")
            
            # Sample version info for testing
            test_version_info = {
                "version": "1.1.0",
                "download_url": "https://example.com/downloads/pyinstaller-gui-1.1.0.zip",
                "details": "Test update with new features"
            }
            
            print(f"Testing with sample version: {test_version_info['version']}")
            
            # Download and apply update
            if 'download_url' in test_version_info:
                success, file_path, error = download_update(test_version_info['download_url'])
                
                if success:
                    apply_success, apply_error = apply_update(file_path)
                    if apply_success:
                        print("Update successfully applied!")
                    else:
                        print(f"Failed to apply update: {apply_error}")
                else:
                    print(f"Failed to download update: {error}")
    else:
        print("Update was successfully applied.") 