"""
Drag and drop support for Enhanced PyInstaller GUI
Implements a custom QListWidget that accepts drag and drop operations for files
"""

import os
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QMessageBox
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DragDropListWidget(QListWidget):
    """List widget with drag and drop support for files."""
    
    def __init__(self, parent=None, allowed_extensions=None):
        """
        Initialize a list widget with drag and drop support.
        
        Args:
            parent: Parent widget
            allowed_extensions: List of allowed file extensions (e.g. ['.py', '.pyw'])
        """
        super().__init__(parent)
        self.parent = parent
        self.allowed_extensions = allowed_extensions or ['.py']
        
        # Enhanced drag and drop setup
        self.setDragEnabled(False)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        # Set appearance
        self.setAlternatingRowColors(True)
        
        # Add delete key support
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        
        # Log initialization
        if hasattr(self.parent, 'log_message'):
            self.parent.log_message("Drag and drop list widget initialized with extensions: " + 
                                   ", ".join(self.allowed_extensions))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for files."""
        # Log the drag enter event for debugging
        if hasattr(self.parent, 'log_message'):
            self.parent.log_message("Drag enter event detected")
        
        # Check for URLs in the mime data
        if event.mimeData().hasUrls():
            # Debug output
            if hasattr(self.parent, 'log_message'):
                urls = [url.toLocalFile() for url in event.mimeData().urls()]
                self.parent.log_message(f"Drag contains files: {', '.join(urls)}")
            
            # Check if at least one file has allowed extension
            valid_files = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.allowed_extensions:
                    valid_files = True
                    break
            
            if valid_files:
                event.acceptProposedAction()
                return
        
        # If we get here, no valid files were found
        event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move events."""
        # Log the drag move event for debugging (only occasionally to avoid spam)
        if hasattr(self.parent, 'log_message') and event.pos().y() % 50 == 0:  # Log only occasionally
            self.parent.log_message("Drag move event at position: {}, {}".format(event.pos().x(), event.pos().y()))
        
        # Make sure we consistently accept the action
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.allowed_extensions:
                    event.acceptProposedAction()
                    return
        
        # If we get here, no valid files were found
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for files."""
        # Log the drop event
        if hasattr(self.parent, 'log_message'):
            self.parent.log_message("File drop event detected")
        
        files_added = 0
        error_files = []
        
        try:
            # Process each URL in the dropped data
            for url in event.mimeData().urls():
                try:
                    file_path = url.toLocalFile()
                    
                    # Log the file being processed
                    if hasattr(self.parent, 'log_message'):
                        self.parent.log_message(f"Processing dropped file: {file_path}")
                    
                    _, ext = os.path.splitext(file_path)
                    
                    # Check if the file exists and has an allowed extension
                    if not os.path.exists(file_path):
                        if hasattr(self.parent, 'log_message'):
                            self.parent.log_message(f"Error: File does not exist: {file_path}")
                        error_files.append(file_path)
                        continue
                    
                    if ext.lower() not in self.allowed_extensions:
                        if hasattr(self.parent, 'log_message'):
                            self.parent.log_message(f"Error: Invalid extension: {ext} for file: {file_path}")
                        error_files.append(file_path)
                        continue
                    
                    # Add the file to the list if it's not already there
                    items = self.findItems(file_path, Qt.MatchExactly)
                    if not items:
                        self.addItem(file_path)
                        files_added += 1
                    else:
                        if hasattr(self.parent, 'log_message'):
                            self.parent.log_message(f"File already in list: {file_path}")
                
                except Exception as e:
                    if hasattr(self.parent, 'log_message'):
                        self.parent.log_message(f"Error processing file: {str(e)}")
                    continue
            
            # Accept the action
            event.acceptProposedAction()
            
            # Show summary
            if hasattr(self.parent, 'log_message'):
                self.parent.log_message(f"Added {files_added} file(s) via drag and drop")
                if error_files:
                    self.parent.log_message(f"Failed to add {len(error_files)} file(s)")
            
            # Show error message if needed
            if error_files and hasattr(self.parent, 'statusBar'):
                self.parent.statusBar().showMessage(
                    f"Some files could not be added. Check file extensions.", 3000
                )
        
        except Exception as e:
            # Log any unexpected errors
            if hasattr(self.parent, 'log_message'):
                self.parent.log_message(f"Unexpected error in drop event: {str(e)}")
            
            # Make sure we still accept the event to avoid UI hanging
            event.acceptProposedAction()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Delete selected items on Delete key
        if event.key() == Qt.Key_Delete:
            self.remove_selected_items()
        else:
            super().keyPressEvent(event)
    
    def remove_selected_items(self):
        """Remove selected items from the list."""
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            self.takeItem(self.row(item))
        
        # Log the action
        if hasattr(self.parent, 'log_message'):
            self.parent.log_message(f"Removed {len(selected_items)} item(s)")
    
    def add_files_dialog(self):
        """Add files using a file dialog."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_filter = "Python Files (*.py *.pyw);;All Files (*.*)"
        files, _ = QFileDialog.getOpenFileNames(self, "Add Python Scripts", "", file_filter)
        
        if files:
            for file_path in files:
                _, ext = os.path.splitext(file_path)
                if ext.lower() in self.allowed_extensions:
                    self.addItem(file_path)
            
            # Log the action
            if hasattr(self.parent, 'log_message'):
                self.parent.log_message(f"Added {len(files)} file(s) via dialog")
    
    def clear(self):
        """Clear all items from the list."""
        super().clear()
        
        # Log the action
        if hasattr(self.parent, 'log_message'):
            self.parent.log_message("Cleared all files")
