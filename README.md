# Layer Attribute Manager

A QGIS plugin for managing and editing attribute tables for all vector layers in one interface.

## Features

- View and edit attribute tables for all vector layers
- Search and filter data across all fields
- Copy/paste data from spreadsheets into attribute tables easily
- Update layers with changes made in the table
- Revert changes back to original values

## Installation

1. Copy the plugin folder to your QGIS plugins directory (by default - C:\Users\[USERNAME]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins) 
2. Enable the plugin in QGIS Plugin Manager
3. The plugin will appear in the toolbar
4. If it does not appear, relaunch QGIS

## Usage

1. Click "Open Attribute Manager" in the toolbar
2. Select a layer from the dropdown
3. Edit data directly in the table
4. Use "Update Layer" to save changes
5. Use "Refresh Layers" to reload data
6. In order to paste data from spreadsheet:
    - select cells you want to copy in spreadsheet
    - copy them with ctrl+c 
    - in layer manager choose layer you want to copy data to
    - click on a cell that corresponds to top left cell of data You are copying, it must be selected
    - click on button "Paste from Spreadsheet"
7. In order to copy data from layer manager into spreadsheet:
    - select data in Layout Attribute Manager
    - click Copy Selection
    - paste data in spreadsheet

## Requirements

- QGIS 3.0 or higher

## If you see room for improvement, contact me:
    kk.at.work@pm.me


## Author

Kacper Kolbusz
