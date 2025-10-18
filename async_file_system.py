"""
Asynchronous file system operations for Enhanced PyInstaller GUI
Provides classes for handling file operations in a non-blocking way
"""

import os
import asyncio
import concurrent.futures
import shutil
import threading
from pathlib import Path
from typing import List, Tuple, Dict, Any, Callable, Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

# Import aiofiles for asynchronous file operations
try:
    import aiofiles
    import aiofiles.os as aio_os
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    print("Warning: aiofiles package not found. Falling back to synchronous operations.")

class FileSystemManager:
    """Manages file system operations with caching and optimization."""
    
    def __init__(self):
        """Initialize the file system manager."""
        self.thread_pool = QThreadPool()
        self.file_cache = {}
        
    def get_file_info(self, file_path):
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File information (name, size, extension, etc.)
        """
        if file_path in self.file_cache:
            return self.file_cache[file_path]
        
        file_info = {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'extension': os.path.splitext(file_path)[1],
            'exists': os.path.exists(file_path),
            'is_dir': os.path.isdir(file_path) if os.path.exists(file_path) else False
        }
        
        self.file_cache[file_path] = file_info
        return file_info
    
    def clear_cache(self):
        """Clear the file cache."""
        self.file_cache = {}
    
    def copy_file_async(self, source, destination, callback=None):
        """
        Copy a file asynchronously.
        
        Args:
            source: Source file path
            destination: Destination file path
            callback: Function to call when the operation is complete
        """
        def copy_worker():
            try:
                shutil.copy2(source, destination)
                if callback:
                    callback(True, None)
            except Exception as e:
                if callback:
                    callback(False, str(e))
        
        threading.Thread(target=copy_worker).start()
    
    def ensure_dir(self, directory):
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path
            
        Returns:
            bool: True if the directory exists or was created, False otherwise
        """
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    def get_directory_size(self, directory):
        """
        Get the total size of a directory.
        
        Args:
            directory: Directory path
            
        Returns:
            int: Total size in bytes
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if not os.path.islink(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

class FileOperationSignals(QObject):
    """Signals for file operations."""
    
    started = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    completed = pyqtSignal(bool, str, str)
    error = pyqtSignal(str)

class FileOperation(QRunnable):
    """Base class for asynchronous file operations."""
    
    def __init__(self, operation_type, source=None, destination=None):
        """
        Initialize the file operation.
        
        Args:
            operation_type: Type of operation (copy, move, delete, etc.)
            source: Source path
            destination: Destination path
        """
        super().__init__()
        self.operation_type = operation_type
        self.source = source
        self.destination = destination
        self.signals = FileOperationSignals()
        
    def run(self):
        """Execute the file operation."""
        self.signals.started.emit(self.operation_type)
        
        try:
            if self.operation_type == "copy":
                self._copy_operation()
            elif self.operation_type == "move":
                self._move_operation()
            elif self.operation_type == "delete":
                self._delete_operation()
            else:
                raise ValueError(f"Unknown operation type: {self.operation_type}")
                
            self.signals.completed.emit(True, self.operation_type, "Operation completed successfully")
            
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.completed.emit(False, self.operation_type, str(e))
    
    def _copy_operation(self):
        """Execute a copy operation."""
        if os.path.isdir(self.source):
            shutil.copytree(self.source, self.destination)
        else:
            shutil.copy2(self.source, self.destination)
    
    def _move_operation(self):
        """Execute a move operation."""
        shutil.move(self.source, self.destination)
    
    def _delete_operation(self):
        """Execute a delete operation."""
        if os.path.isdir(self.source):
            shutil.rmtree(self.source)
        else:
            os.remove(self.source)

class AsyncFileProcessor:
    """Manages asynchronous file operations."""
    
    def __init__(self):
        """Initialize the async file processor."""
        self.thread_pool = QThreadPool()
        self.operations = []
        
    def add_operation(self, operation):
        """
        Add a file operation to the queue.
        
        Args:
            operation: FileOperation instance
        """
        self.operations.append(operation)
        self.thread_pool.start(operation)
    
    def copy_file(self, source, destination, callbacks=None):
        """
        Copy a file asynchronously.
        
        Args:
            source: Source file path
            destination: Destination file path
            callbacks: Dictionary of callback functions
        """
        operation = FileOperation("copy", source, destination)
        
        if callbacks:
            if 'started' in callbacks:
                operation.signals.started.connect(callbacks['started'])
            if 'progress' in callbacks:
                operation.signals.progress.connect(callbacks['progress'])
            if 'completed' in callbacks:
                operation.signals.completed.connect(callbacks['completed'])
            if 'error' in callbacks:
                operation.signals.error.connect(callbacks['error'])
        
        self.add_operation(operation)
    
    def move_file(self, source, destination, callbacks=None):
        """
        Move a file asynchronously.
        
        Args:
            source: Source file path
            destination: Destination file path
            callbacks: Dictionary of callback functions
        """
        operation = FileOperation("move", source, destination)
        
        if callbacks:
            if 'started' in callbacks:
                operation.signals.started.connect(callbacks['started'])
            if 'progress' in callbacks:
                operation.signals.progress.connect(callbacks['progress'])
            if 'completed' in callbacks:
                operation.signals.completed.connect(callbacks['completed'])
            if 'error' in callbacks:
                operation.signals.error.connect(callbacks['error'])
        
        self.add_operation(operation)
    
    def delete_file(self, file_path, callbacks=None):
        """
        Delete a file asynchronously.
        
        Args:
            file_path: Path to the file to delete
            callbacks: Dictionary of callback functions
        """
        operation = FileOperation("delete", file_path)
        
        if callbacks:
            if 'started' in callbacks:
                operation.signals.started.connect(callbacks['started'])
            if 'progress' in callbacks:
                operation.signals.progress.connect(callbacks['progress'])
            if 'completed' in callbacks:
                operation.signals.completed.connect(callbacks['completed'])
            if 'error' in callbacks:
                operation.signals.error.connect(callbacks['error'])
        
        self.add_operation(operation)
