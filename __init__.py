# -*- coding: utf-8 -*-
"""
Layer Attribute Manager Plugin for QGIS
A powerful plugin to manage and edit attribute tables for all layers in one interface.
"""

def classFactory(iface):
    """Load AttributeManagerPlugin class from file main_plugin.
    
    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    try:
        from .main_plugin import AttributeManagerPlugin
        return AttributeManagerPlugin(iface)
    except ImportError as e:
        # Log the import error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to import AttributeManagerPlugin: {e}")
        raise
    except Exception as e:
        # Log any other errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in classFactory: {e}")
        raise
