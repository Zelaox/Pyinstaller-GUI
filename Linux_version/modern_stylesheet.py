"""
Modern stylesheet for Enhanced PyInstaller GUI
Provides light and dark themes with consistent styling
"""

import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QSettings

# Define stylesheet constants
LIGHT_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #f8f8f8;
    color: #444444;
}

QMenuBar {
    background-color: #f8f8f8;
    color: #444444;
}

QMenuBar::item:selected {
    background-color: #eaeaea;
}

QMenu {
    background-color: #f8f8f8;
    color: #444444;
}

QMenu::item:selected {
    background-color: #eaeaea;
}

QToolBar {
    background-color: #f8f8f8;
    border-bottom: 1px solid #e8e8e8;
    spacing: 6px;
}

QPushButton {
    background-color: #e8e8e8;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    padding: 5px 10px;
    color: #444444;
}

QPushButton:hover {
    background-color: #dedede;
}

QPushButton:pressed {
    background-color: #d0d0d0;
}

QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #fcfcfc;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    padding: 3px;
    color: #444444;
}

QListWidget, QTreeWidget {
    background-color: #fcfcfc;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    alternate-background-color: #f5f5f5;
    color: #444444;
}

QStatusBar {
    background-color: #f8f8f8;
    color: #777777;
}

QProgressBar {
    border: 1px solid #d8d8d8;
    border-radius: 4px;
    text-align: center;
    background-color: #fcfcfc;
}

QProgressBar::chunk {
    background-color: #72a1e8;
}

QScrollBar:vertical {
    border: none;
    background-color: #f0f0f0;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f0f0f0;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #e0e0e0;
    padding: 5px 10px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-bottom: none;
}

QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
"""

DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #323232;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #323232;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #424242;
}

QMenu {
    background-color: #323232;
    color: #e0e0e0;
}

QMenu::item:selected {
    background-color: #424242;
}

QToolBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    spacing: 6px;
}

QPushButton {
    background-color: #404040;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px 10px;
    color: #e0e0e0;
}

QPushButton:hover {
    background-color: #505050;
}

QPushButton:pressed {
    background-color: #606060;
}

QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #3d3d3d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 3px;
    color: #e0e0e0;
}

QListWidget, QTreeWidget {
    background-color: #3d3d3d;
    border: 1px solid #555555;
    border-radius: 4px;
    alternate-background-color: #353535;
    color: #e0e0e0;
}

QStatusBar {
    background-color: #2d2d2d;
    color: #a0a0a0;
}

QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    background-color: #3d3d3d;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #4a86e8;
}

QScrollBar:vertical {
    border: none;
    background-color: #2d2d2d;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #5d5d5d;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6d6d6d;
}

QScrollBar:horizontal {
    border: none;
    background-color: #2d2d2d;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #5d5d5d;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6d6d6d;
}

QTabWidget::pane {
    border: 1px solid #555555;
    border-radius: 4px;
    }
    
    QTabBar::tab {
    background-color: #404040;
    padding: 5px 10px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #3d3d3d;
    border: 1px solid #555555;
    border-bottom: none;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}
"""

# Icon paths for different themes
ICONS = {
    "light": {
        "add_files": "icons/light/add_files.png",
        "package": "icons/light/package.png",
        "installer": "icons/light/installer.png",
        "settings": "icons/light/settings.png",
        "profiles": "icons/light/profiles.png",
        "help": "icons/light/help.png"
    },
    "dark": {
        "add_files": "icons/dark/add_files.png",
        "package": "icons/dark/package.png",
        "installer": "icons/dark/installer.png",
        "settings": "icons/dark/settings.png",
        "profiles": "icons/dark/profiles.png",
        "help": "icons/dark/help.png"
    }
}

class StyleManager:
    """Manages application styles and themes."""
    
    def __init__(self):
        """Initialize the style manager."""
        self.current_theme = "light"
        self.settings = QSettings("EnhancedPyInstallerGUI", "AppSettings")
        
    def apply_stylesheet(self, app, theme=None):
        """
        Apply a stylesheet to the application.
        
        Args:
            app: QApplication instance
            theme: Theme name ("light" or "dark")
        """
        if theme is None:
            theme = self.settings.value("Theme", "light")
        
        self.current_theme = theme
        
        if theme == "dark":
            app.setStyleSheet(DARK_STYLESHEET)
            self._set_dark_palette(app)
        elif theme == "matrix":
            self._set_matrix_theme(app)
        else:  # Default to light theme
            app.setStyleSheet(LIGHT_STYLESHEET)
            self._set_light_palette(app)
            
        # Save the theme setting
        self.settings.setValue("Theme", theme)
    
    def _set_light_palette(self, app):
        """Set light color palette."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(248, 248, 248))
        palette.setColor(QPalette.WindowText, QColor(68, 68, 68))
        palette.setColor(QPalette.Base, QColor(252, 252, 252))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(252, 252, 252))
        palette.setColor(QPalette.ToolTipText, QColor(68, 68, 68))
        palette.setColor(QPalette.Text, QColor(68, 68, 68))
        palette.setColor(QPalette.Button, QColor(232, 232, 232))
        palette.setColor(QPalette.ButtonText, QColor(68, 68, 68))
        palette.setColor(QPalette.Link, QColor(70, 130, 200))
        palette.setColor(QPalette.Highlight, QColor(114, 161, 232))
        palette.setColor(QPalette.HighlightedText, QColor(252, 252, 252))
        
        app.setPalette(palette)
    
    def _set_dark_palette(self, app):
        """Set dark color palette."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(50, 50, 50))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(66, 66, 66))
        palette.setColor(QPalette.AlternateBase, QColor(58, 58, 58))
        palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(69, 69, 69))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.Link, QColor(106, 150, 232))
        palette.setColor(QPalette.Highlight, QColor(106, 150, 232))
        palette.setColor(QPalette.HighlightedText, QColor(235, 235, 235))
        
        app.setPalette(palette)
    
    def _set_matrix_theme(self, app):
        """Set matrix-inspired theme."""
        matrix_stylesheet = """
            QMainWindow, QDialog {
                background-color: #0a120a;
                color: #88cc88;
            }
            
            QMenuBar, QMenu, QToolBar {
                background-color: #0a120a;
                color: #88cc88;
                border: 1px solid #1a3a1a;
            }
            
            QMenuBar::item:selected, QMenu::item:selected {
                background-color: #1a321a;
            }
            
            QPushButton {
                background-color: #1a321a;
                border: 1px solid #2a5a2a;
                border-radius: 4px;
                padding: 5px 10px;
                color: #88cc88;
            }
            
            QPushButton:hover {
                background-color: #1e3a1e;
            }
            
            QPushButton:pressed {
                background-color: #234023;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QListWidget, QTreeWidget {
                background-color: #0e1e0e;
                border: 1px solid #2a5a2a;
                color: #88cc88;
            }
            
            QProgressBar {
                border: 1px solid #2a5a2a;
                background-color: #0a120a;
                text-align: center;
                color: #88cc88;
            }
            
            QProgressBar::chunk {
                background-color: #3a7a3a;
            }
            
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #2a5a2a;
            }
            
            QStatusBar {
                background-color: #0a120a;
                color: #6aaa6a;
            }

            QTabWidget::pane {
                border: 1px solid #2a5a2a;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #1a321a;
                padding: 5px 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #88cc88;
            }
            
            QTabBar::tab:selected {
                background-color: #234023;
                border: 1px solid #2a5a2a;
                border-bottom: none;
            }
            
            QGroupBox {
                border: 1px solid #2a5a2a;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: #88cc88;
            }
        """
        
        app.setStyleSheet(matrix_stylesheet)
        
        # Create palette with softer, eye-friendly colors
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(10, 18, 10))
        palette.setColor(QPalette.WindowText, QColor(136, 204, 136))
        palette.setColor(QPalette.Base, QColor(14, 30, 14))
        palette.setColor(QPalette.AlternateBase, QColor(18, 36, 18))
        palette.setColor(QPalette.ToolTipBase, QColor(10, 18, 10))
        palette.setColor(QPalette.ToolTipText, QColor(136, 204, 136))
        palette.setColor(QPalette.Text, QColor(136, 204, 136))
        palette.setColor(QPalette.Button, QColor(26, 50, 26))
        palette.setColor(QPalette.ButtonText, QColor(136, 204, 136))
        palette.setColor(QPalette.Link, QColor(106, 170, 106))
        palette.setColor(QPalette.Highlight, QColor(58, 122, 58))
        palette.setColor(QPalette.HighlightedText, QColor(200, 240, 200))
        
        app.setPalette(palette)

    def get_icon_path(self, icon_name):
        """
        Get the appropriate icon path for the current theme.
        
        Args:
            icon_name: Icon name as defined in the ICONS dictionary
            
        Returns:
            str: Path to the icon file
        """
        theme = self.current_theme
        if theme not in ICONS or icon_name not in ICONS[theme]:
            theme = "light"  # Fallback to light theme
        
        return ICONS[theme].get(icon_name, "")
