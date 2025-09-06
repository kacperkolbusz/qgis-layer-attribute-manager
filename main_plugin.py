# -*- coding: utf-8 -*-
"""
Layer Attribute Manager Plugin for QGIS
A powerful plugin to manage and edit attribute tables for all layers in one interface.
"""

import os
import logging
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QToolBar
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField
from qgis.utils import iface
from .attribute_manager_dialog import AttributeManagerDialog


class AttributeManagerPlugin:
    """Main plugin class for managing layer attributes."""

    def __init__(self, iface):
        """Initialize the plugin.
        
        :param iface: A QGIS interface instance.
        :type iface: QgisInterface
        """
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.project = QgsProject.instance()
        
        # Plugin state
        self.dialog = None
        self.toolbar = None
        self.action_open_manager = None
        self.action_settings = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        

    def initGui(self):
        """Called when the plugin is loaded. This method is required by QGIS."""
        try:
            # Initialize the plugin
            self.init_plugin()
            self.logger.info("Attribute Manager Plugin initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Attribute Manager Plugin: {str(e)}")
            # Show error to user but don't crash the plugin
            QMessageBox.critical(None, "Plugin Error", 
                                f"Failed to initialize Attribute Manager Plugin:\n{str(e)}\n\n"
                                "The plugin may not work correctly. Please check the QGIS log for details.")

    def init_plugin(self):
        """Initialize the plugin by adding toolbar and menu items."""
        try:
            # Create toolbar
            self.toolbar = self.iface.addToolBar('Layer Attribute Manager')
            self.toolbar.setObjectName('AttributeManagerToolbar')
            
            # Create actions with icon fallbacks
            plugin_dir = os.path.dirname(__file__)
            
            # Try to load icons, use fallback if they fail
            try:
                main_icon = QIcon(os.path.join(plugin_dir, 'icons', 'main.ico'))
                if main_icon.isNull():
                    # Create a fallback icon
                    main_icon = QIcon()
                    self.logger.warning("Main icon could not be loaded, using fallback")
            except Exception as e:
                self.logger.warning(f"Could not load main icon: {e}")
                main_icon = QIcon()
            
            try:
                settings_icon = QIcon(os.path.join(plugin_dir, 'icons', 'settings.ico'))
                if settings_icon.isNull():
                    # Create a fallback icon
                    settings_icon = QIcon()
                    self.logger.warning("Settings icon could not be loaded, using fallback")
            except Exception as e:
                self.logger.warning(f"Could not load settings icon: {e}")
                settings_icon = QIcon()
            
            # Create actions with fallback icons
            self.action_open_manager = QAction(
                main_icon,
                'Open Attribute Manager',
                self.iface.mainWindow()
            )
            self.action_open_manager.setToolTip('Open the Layer Attribute Manager dialog')
            self.action_open_manager.triggered.connect(self.open_attribute_manager)
            
            self.action_settings = QAction(
                settings_icon,
                'Settings',
                self.iface.mainWindow()
            )
            self.action_settings.setToolTip('Open plugin settings')
            self.action_settings.triggered.connect(self.show_settings)
            
            # Add actions to toolbar
            self.toolbar.addAction(self.action_open_manager)
            self.toolbar.addAction(self.action_settings)
            
            # Add to menu
            self.iface.addPluginToMenu('Layer Attribute Manager', self.action_open_manager)
            self.iface.addPluginToMenu('Layer Attribute Manager', self.action_settings)
            
            # Connect project signals with error handling
            try:
                if hasattr(self, 'project') and self.project:
                    self.project.layersAdded.connect(self.on_layer_added)
                    self.project.layersRemoved.connect(self.on_layer_removed)
                    self.logger.info("Project signals connected successfully")
                else:
                    self.logger.warning("Project not available, signals not connected")
            except Exception as e:
                self.logger.warning(f"Could not connect project signals: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in init_plugin: {str(e)}")
            raise  # Re-raise to be caught by initGui

    def open_attribute_manager(self):
        """Open the attribute manager dialog."""
        try:
            if not self.dialog:
                self.dialog = AttributeManagerDialog(self.iface.mainWindow())
            
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()
            
        except Exception as e:
            self.logger.error(f"Error opening attribute manager: {str(e)}")
            QMessageBox.critical(None, 'Error Opening Manager', 
                                f'Error opening attribute manager:\n{str(e)}')

    def show_settings(self):
        """Show the plugin settings dialog."""
        try:
            from .settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(self.iface.mainWindow())
            settings_dialog.exec_()
        except Exception as e:
            self.logger.error(f"Error opening settings: {str(e)}")
            QMessageBox.critical(None, 'Error Opening Settings', 
                                f'Error opening settings:\n{str(e)}')

    def on_layer_added(self, layers):
        """Handle when new layers are added to the project."""
        if self.dialog and self.dialog.isVisible():
            self.dialog.refresh_layers()

    def on_layer_removed(self, layers):
        """Handle when layers are removed from the project."""
        if self.dialog and self.dialog.isVisible():
            self.dialog.refresh_layers()
    

    def unload(self):
        """Unload the plugin."""
        try:
            # Remove toolbar
            if hasattr(self, 'toolbar') and self.toolbar:
                try:
                    self.iface.removeToolBar(self.toolbar)
                    self.logger.info("Toolbar removed successfully")
                except Exception as e:
                    self.logger.warning(f"Could not remove toolbar: {e}")
            
            # Remove menu items
            if hasattr(self, 'action_open_manager') and self.action_open_manager:
                try:
                    self.iface.removePluginMenu('Layer Attribute Manager', self.action_open_manager)
                except Exception as e:
                    self.logger.warning(f"Could not remove open manager menu: {e}")
            
            if hasattr(self, 'action_settings') and self.action_settings:
                try:
                    self.iface.removePluginMenu('Layer Attribute Manager', self.action_settings)
                except Exception as e:
                    self.logger.warning(f"Could not remove settings menu: {e}")
            
            # Disconnect signals
            if hasattr(self, 'project') and self.project:
                try:
                    self.project.layersAdded.disconnect(self.on_layer_added)
                    self.project.layersRemoved.disconnect(self.on_layer_removed)
                    self.logger.info("Project signals disconnected successfully")
                except Exception as e:
                    self.logger.warning(f"Could not disconnect project signals: {e}")
            
            # Close dialog if open
            if hasattr(self, 'dialog') and self.dialog:
                try:
                    self.dialog.close()
                    self.dialog = None
                    self.logger.info("Dialog closed successfully")
                except Exception as e:
                    self.logger.warning(f"Could not close dialog: {e}")
            
            
            self.logger.info("Attribute Manager Plugin unloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error during plugin unload: {str(e)}")
            # Don't raise the exception - just log it


# Test import - this helps with debugging
if __name__ == "__main__":
    print("AttributeManagerPlugin module loaded successfully")
