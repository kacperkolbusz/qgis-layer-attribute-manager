#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Excel Sync Plugin for QGIS.
This script helps with development setup and testing.
"""

import os
import sys
import shutil
from pathlib import Path

def get_qgis_plugins_dir():
    """Get the QGIS plugins directory for the current user."""
    if sys.platform == "win32":
        # Windows
        appdata = os.environ.get('APPDATA', '')
        return os.path.join(appdata, 'QGIS', 'QGIS3', 'profiles', 'default', 'python', 'plugins')
    elif sys.platform == "darwin":
        # macOS
        home = os.path.expanduser("~")
        return os.path.join(home, 'Library', 'Application Support', 'QGIS', 'QGIS3', 'profiles', 'default', 'python', 'plugins')
    else:
        # Linux
        home = os.path.expanduser("~")
        return os.path.join(home, '.local', 'share', 'QGIS', 'QGIS3', 'profiles', 'default', 'python', 'plugins')

def install_plugin():
    """Install the plugin to QGIS plugins directory."""
    current_dir = Path(__file__).parent
    plugins_dir = get_qgis_plugins_dir()
    
    if not os.path.exists(plugins_dir):
        print(f"QGIS plugins directory not found: {plugins_dir}")
        print("Please ensure QGIS is installed and has been run at least once.")
        return False
    
    target_dir = os.path.join(plugins_dir, 'excel_sync_plugin')
    
    try:
        # Remove existing installation if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
            print(f"Removed existing installation from: {target_dir}")
        
        # Copy plugin files
        shutil.copytree(current_dir, target_dir)
        print(f"Plugin installed to: {target_dir}")
        
        # Remove setup.py from target (not needed in QGIS)
        setup_file = os.path.join(target_dir, 'setup.py')
        if os.path.exists(setup_file):
            os.remove(setup_file)
        
        print("Installation completed successfully!")
        print("Restart QGIS and enable the plugin in Plugins → Manage and Install Plugins")
        return True
        
    except Exception as e:
        print(f"Installation failed: {str(e)}")
        return False

def uninstall_plugin():
    """Uninstall the plugin from QGIS plugins directory."""
    plugins_dir = get_qgis_plugins_dir()
    target_dir = os.path.join(plugins_dir, 'excel_sync_plugin')
    
    if os.path.exists(target_dir):
        try:
            shutil.rmtree(target_dir)
            print(f"Plugin uninstalled from: {target_dir}")
            return True
        except Exception as e:
            print(f"Uninstallation failed: {str(e)}")
            return False
    else:
        print("Plugin not found in QGIS plugins directory.")
        return False

def check_dependencies():
    """Check if required Python dependencies are installed."""
    required_packages = ['openpyxl', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("All required packages are installed.")
        return True

def main():
    """Main setup function."""
    print("Excel Sync Plugin for QGIS - Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            if check_dependencies():
                install_plugin()
            else:
                print("Please install missing dependencies first.")
        elif command == "uninstall":
            uninstall_plugin()
        elif command == "check":
            check_dependencies()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: install, uninstall, check")
    else:
        print("Available commands:")
        print("  install    - Install the plugin to QGIS")
        print("  uninstall  - Remove the plugin from QGIS")
        print("  check      - Check if dependencies are installed")
        print("\nExample: python setup.py install")

if __name__ == "__main__":
    main()
