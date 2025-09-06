# -*- coding: utf-8 -*-
"""
Settings Dialog for Layer Attribute Manager Plugin
Provides a blank settings interface for future configuration options.
"""

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QMessageBox, QComboBox, QGroupBox)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont


class SettingsDialog(QDialog):
    """Settings dialog for the Attribute Manager plugin."""

    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle('Layer Attribute Manager - Settings')
        self.setModal(True)
        self.resize(400, 300)
        
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel('Settings')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        
        # Placeholder content
        self.placeholder_label = QLabel('Settings options will be added here in future versions.')
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(self.placeholder_label)
        
        # Add some spacing
        layout.addStretch()
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        # OK button
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.ok_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        event.accept()
