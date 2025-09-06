# -*- coding: utf-8 -*-
"""
Attribute Manager Dialog for QGIS.
Provides a comprehensive interface for managing and editing attribute tables.
"""

import os
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QComboBox, QPushButton, QTextEdit, QGroupBox,
                                 QCheckBox, QProgressBar, QMessageBox,
                                 QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                                 QTabWidget, QWidget, QLineEdit, QSpinBox, QFormLayout,
                                 QMenu, QApplication)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QTimer
from qgis.PyQt.QtGui import QFont, QIcon
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, NULL


class AttributeTableWidget(QWidget):
    """Widget for displaying and editing a single layer's attribute table."""
    
    def __init__(self, layer, parent=None):
        """Initialize the attribute table widget.
        
        :param layer: QGIS vector layer
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.layer = layer
        self.original_data = {}  # Store original values
        self.changed_cells = set()  # Track changed cells
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Layer info header
        header_layout = QHBoxLayout()
        self.layer_label = QLabel(f"Layer: {self.layer.name()}")
        self.features_label = QLabel(f"Features: {self.layer.featureCount()}")
        self.fields_label = QLabel(f"Fields: {len(self.layer.fields())}")
        header_layout.addWidget(self.layer_label)
        header_layout.addWidget(self.features_label)
        header_layout.addWidget(self.fields_label)
        header_layout.addStretch()
        
        
        # Update button
        self.update_btn = QPushButton('Update Layer')
        self.update_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.update_btn.clicked.connect(self.update_layer)
        header_layout.addWidget(self.update_btn)
        
        # Revert button
        self.revert_btn = QPushButton('Revert Changes')
        self.revert_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        self.revert_btn.clicked.connect(self.revert_changes)
        header_layout.addWidget(self.revert_btn)
        
        # Copy/Paste buttons
        self.copy_btn = QPushButton('Copy Selection')
        self.copy_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        self.copy_btn.setToolTip('Copy selected cells to clipboard')
        self.copy_btn.clicked.connect(self.copy_selection)
        header_layout.addWidget(self.copy_btn)
        
        self.paste_btn = QPushButton('Paste from Spreadsheet')
        self.paste_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        self.paste_btn.setToolTip('Paste data from clipboard (Excel/CSV format)')
        self.paste_btn.clicked.connect(self.paste_from_excel)
        header_layout.addWidget(self.paste_btn)
        
        layout.addLayout(header_layout)
        
        
        # Search and filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Search:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search in all fields...')
        self.search_input.textChanged.connect(self.filter_data)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel('Field:'))
        self.field_filter = QComboBox()
        self.field_filter.addItem('All Fields')
        self.field_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.field_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Attribute table
        try:
            self.table = QTableWidget()
            self.table.setAlternatingRowColors(True)
            self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed | QTableWidget.AnyKeyPressed)
            self.table.setSelectionBehavior(QTableWidget.SelectItems)  # Use SelectItems for compatibility
            self.table.setSelectionMode(QTableWidget.ContiguousSelection)  # Use ContiguousSelection for better compatibility
            self.table.itemChanged.connect(self.on_cell_changed)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.show_context_menu)
            
            # Enable drag selection for better user experience
            self.table.setDragEnabled(True)
            self.table.setDragDropMode(QTableWidget.NoDragDrop)
            
            # Add keyboard shortcuts
            self.table.keyPressEvent = self.table_key_press_event
            
            # Connect selection change signal to update visual feedback
            self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
            
        except Exception as e:
            # Fallback to basic table if advanced features fail
            print(f"Warning: Advanced table features not available: {e}")
            self.table = QTableWidget()
            self.table.setAlternatingRowColors(True)
            self.table.setEditTriggers(QTableWidget.DoubleClicked)
            self.table.setSelectionBehavior(QTableWidget.SelectItems)
            self.table.setSelectionMode(QTableWidget.SingleSelection)
            self.table.itemChanged.connect(self.on_cell_changed)
        
        layout.addWidget(self.table)
        
        # Status bar
        self.status_label = QLabel('Ready')
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load the layer's attribute data into the table."""
        try:
            # Get fields
            fields = self.layer.fields()
            field_names = [field.name() for field in fields]
            
            # Update field filter
            self.field_filter.clear()
            self.field_filter.addItem('All Fields')
            self.field_filter.addItems(field_names)
            
            # Setup table
            self.table.setColumnCount(len(field_names))
            self.table.setHorizontalHeaderLabels(field_names)
            
            # Get features
            features = list(self.layer.getFeatures())
            self.table.setRowCount(len(features))
            
            # Populate table
            for row, feature in enumerate(features):
                for col, field_name in enumerate(field_names):
                    value = feature[field_name]
                    
                    # Handle NULL values
                    if value == NULL or value is None:
                        display_value = ""
                    else:
                        display_value = str(value)
                    
                    item = QTableWidgetItem(display_value)
                    # Ensure the item is editable
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table.setItem(row, col, item)
                    
                    # Store original value
                    self.original_data[(row, col)] = display_value
            
            # Auto-resize columns
            self.table.resizeColumnsToContents()
            
            # Ensure all cells are editable
            self._make_all_cells_editable()
            
            self.status_label.setText(f'Loaded {len(features)} features with {len(field_names)} fields')
            
        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")
            QMessageBox.critical(self, 'Error Loading Data', f"Failed to load attributes:\n{str(e)}")
    
    def filter_data(self):
        """Filter the table data based on search text and field selection."""
        search_text = self.search_input.text().lower()
        selected_field = self.field_filter.currentText()
        
        for row in range(self.table.rowCount()):
            row_visible = False
            
            for col in range(self.table.columnCount()):
                if selected_field == 'All Fields' or self.table.horizontalHeaderItem(col).text() == selected_field:
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_visible = True
                        break
            
            self.table.setRowHidden(row, not row_visible)
        
        visible_rows = sum(1 for row in range(self.table.rowCount()) if not self.table.isRowHidden(row))
        self.status_label.setText(f'Showing {visible_rows} of {self.table.rowCount()} features')
    
    
    def _make_all_cells_editable(self):
        """Ensure all table cells are editable."""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
    
    def update_layer(self):
        """Update the QGIS layer with changes made in the table."""
        try:
            # Check if layer is editable
            if not self.layer.isEditable():
                reply = QMessageBox.question(
                    self,
                    "Layer Not Editable",
                    f"The layer '{self.layer.name()}' is not in edit mode. Would you like to start editing?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.layer.startEditing()
                else:
                    return
            
            # Get all features from the layer
            features = list(self.layer.getFeatures())
            fields = self.layer.fields()
            field_names = [field.name() for field in fields]
            
            # Track changes
            changes_made = 0
            
            # Update each feature
            for row in range(self.table.rowCount()):
                if row < len(features):
                    feature = features[row]
                    feature_changed = False
                    
                    # Update each field
                    for col, field_name in enumerate(field_names):
                        if col < self.table.columnCount():
                            item = self.table.item(row, col)
                            if item:
                                new_value = item.text().strip()
                                old_value = feature[field_name]
                                
                                # Convert value based on field type
                                converted_value = self._convert_value_for_field(new_value, fields[col])
                                
                                # Check if value actually changed
                                if converted_value != old_value:
                                    feature.setAttribute(field_name, converted_value)
                                    feature_changed = True
                    
                    # If feature was changed, update it
                    if feature_changed:
                        self.layer.updateFeature(feature)
                        changes_made += 1
            
            # Commit changes
            if changes_made > 0:
                success = self.layer.commitChanges()
                if success:
                    QMessageBox.information(
                        self,
                        "Update Successful",
                        f"Successfully updated {changes_made} features in layer '{self.layer.name()}'"
                    )
                    self.status_label.setText(f"Updated {changes_made} features successfully")
                    
                    # Refresh the data to show current values
                    self.load_data()
                else:
                    QMessageBox.critical(
                        self,
                        "Update Failed",
                        f"Failed to commit changes to layer '{self.layer.name()}'. Check the QGIS message log for details."
                    )
                    self.status_label.setText("Update failed - check QGIS message log")
            else:
                QMessageBox.information(
                    self,
                    "No Changes",
                    "No changes were detected in the attribute table."
                )
                self.status_label.setText("No changes detected")
                
        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to update layer:\n{str(e)}")
            self.status_label.setText(f"Update error: {str(e)}")
    
    def _convert_value_for_field(self, value, field):
        """Convert a string value to the appropriate type for a field."""
        try:
            if value == "" or value.lower() in ["null", "none", ""]:
                return NULL
            
            field_type = field.type()
            
            # Handle different field types
            if field_type in [1, 2]:  # Integer types
                return int(value) if value else NULL
            elif field_type in [3, 4]:  # Double/Real types
                return float(value) if value else NULL
            elif field_type == 6:  # String type
                return value if value else NULL
            elif field_type == 10:  # Date type
                from datetime import datetime
                return datetime.strptime(value, "%Y-%m-%d").date() if value else NULL
            else:
                # For other types, try to return as string
                return value if value else NULL
                
        except (ValueError, TypeError):
            # If conversion fails, return the original value
            return value
    
    def on_cell_changed(self, item):
        """Track when a cell value changes."""
        if item:
            row = item.row()
            col = item.column()
            new_value = item.text()
            original_value = self.original_data.get((row, col), "")
            
            if new_value != original_value:
                self.changed_cells.add((row, col))
                # Highlight changed cell
                item.setBackground(Qt.yellow)
            else:
                self.changed_cells.discard((row, col))
                # Reset background
                item.setBackground(Qt.white)
    
    def on_selection_changed(self, selected, deselected):
        """Handle selection changes to provide visual feedback."""
        try:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                total_cells = sum((range.bottomRow() - range.topRow() + 1) * 
                                (range.rightColumn() - range.leftColumn() + 1) 
                                for range in selected_ranges)
                
                if total_cells == 1:
                    self.status_label.setText("1 cell selected - ready to copy or edit")
                else:
                    range_info = []
                    for i, range_obj in enumerate(selected_ranges):
                        rows = range_obj.bottomRow() - range_obj.topRow() + 1
                        cols = range_obj.rightColumn() - range_obj.leftColumn() + 1
                        range_info.append(f"{rows}×{cols}")
                    
                    self.status_label.setText(f"{total_cells} cells selected across {len(selected_ranges)} range(s): {', '.join(range_info)} - ready to copy")
            else:
                self.status_label.setText("No cells selected")
                
        except Exception as e:
            # Don't show error for selection changes, just log it
            pass
    
    def revert_changes(self):
        """Revert all changes back to original values."""
        try:
            reply = QMessageBox.question(
                self,
                "Revert Changes",
                "Are you sure you want to revert all changes? This cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Revert each changed cell
                for row, col in self.changed_cells:
                    item = self.table.item(row, col)
                    if item:
                        original_value = self.original_data.get((row, col), "")
                        item.setText(original_value)
                        item.setBackground(Qt.white)
                
                # Clear changed cells set
                self.changed_cells.clear()
                
                QMessageBox.information(self, "Revert Complete", "All changes have been reverted.")
                self.status_label.setText("Changes reverted successfully")
                
        except Exception as e:
            QMessageBox.critical(self, "Revert Error", f"Failed to revert changes:\n{str(e)}")
            self.status_label.setText(f"Revert error: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for the table."""
        context_menu = QMenu()
        
        # Add "Edit Cell" action
        edit_action = context_menu.addAction("Edit Cell")
        edit_action.triggered.connect(self.edit_current_cell)
        
        context_menu.addSeparator()
        
        # Add "Copy Selection" action
        copy_action = context_menu.addAction("Copy Selection")
        copy_action.triggered.connect(self.copy_selection)
        
        # Add "Paste from Spreadsheet" action
        paste_action = context_menu.addAction("Paste from Spreadsheet")
        paste_action.triggered.connect(self.paste_from_excel)
        
        context_menu.addSeparator()
        
        # Add "Make All Editable" action
        make_editable_action = context_menu.addAction("Make All Cells Editable")
        make_editable_action.triggered.connect(self._make_all_cells_editable)
        
        # Show the context menu
        context_menu.exec_(self.table.mapToGlobal(position))
    
    def edit_current_cell(self):
        """Start editing the current cell."""
        current_item = self.table.currentItem()
        if current_item:
            self.table.editItem(current_item)
    
    def table_key_press_event(self, event):
        """Handle keyboard events for the table."""
        if event.key() == Qt.Key_F2:
            # F2 key starts editing
            self.edit_current_cell()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter key starts editing
            self.edit_current_cell()
        elif event.matches(Qt.CTRL + Qt.Key_C):
            # Ctrl+C for copy
            self.copy_selection()
        elif event.matches(Qt.CTRL + Qt.Key_V):
            # Ctrl+V for paste
            self.paste_from_excel()
        else:
            # Call the original keyPressEvent
            QTableWidget.keyPressEvent(self.table, event)
    
    def copy_selection(self):
        """Copy selected cells to clipboard in Excel-compatible format."""
        try:
            selected_ranges = self.table.selectedRanges()
            if not selected_ranges:
                QMessageBox.information(self, "Copy", "Please select cells to copy first.\n\n"
                                   "You can select multiple cells by:\n"
                                   "• Clicking and dragging to select a range\n"
                                   "• Holding Ctrl while clicking to select individual cells\n"
                                   "• Holding Shift while clicking to extend selection")
                return
            
            clipboard_text = ""
            total_cells = 0
            
            for selected_range in selected_ranges:
                for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                    row_data = []
                    for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                        item = self.table.item(row, col)
                        cell_text = item.text() if item else ""
                        # Escape quotes and wrap in quotes if contains comma or newline
                        if "," in cell_text or "\n" in cell_text or '"' in cell_text:
                            cell_text = f'"{cell_text.replace('"', '""')}"'
                        row_data.append(cell_text)
                        total_cells += 1
                    clipboard_text += "\t".join(row_data) + "\n"
            
            clipboard_text = clipboard_text.strip()
            QApplication.clipboard().setText(clipboard_text)
            
            # Show detailed success message
            range_info = []
            for i, range_obj in enumerate(selected_ranges):
                rows = range_obj.bottomRow() - range_obj.topRow() + 1
                cols = range_obj.rightColumn() - range_obj.leftColumn() + 1
                range_info.append(f"Range {i+1}: {rows}×{cols} cells")
            
            QMessageBox.information(self, "Copy Successful", 
                                  f"✅ Successfully copied {total_cells} cells to clipboard!\n\n"
                                  f"Selection details:\n" + "\n".join(range_info) + "\n\n"
                                  "📋 Data is now in your clipboard and ready to paste into your spreadsheet application!\n"
                                  "💡 Tip: In your spreadsheet, paste with Ctrl+V or right-click → Paste")
            
            self.status_label.setText(f"✅ Copied {total_cells} cells to clipboard")
            
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy selection:\n{str(e)}")
            self.status_label.setText(f"❌ Copy error: {str(e)}")
    
    def paste_from_excel(self):
        """Paste data from clipboard (spreadsheet format) into the table."""
        try:
            clipboard_text = QApplication.clipboard().text()
            if not clipboard_text.strip():
                QMessageBox.information(self, "Paste", "No data found in clipboard.\n\n"
                                   "Please copy data from your spreadsheet application first, then try pasting.")
                return
            
            # Get current selection
            selected_ranges = self.table.selectedRanges()
            if not selected_ranges:
                QMessageBox.information(self, "Paste", "Please select a starting cell first.\n\n"
                                   "Click on the cell where you want to paste the data.")
                return
            
            start_row = selected_ranges[0].topRow()
            start_col = selected_ranges[0].leftColumn()
            
            # Parse clipboard data
            rows = clipboard_text.strip().split('\n')
            if not rows:
                return
            
            # Count total cells to be pasted
            total_cells = 0
            for row in rows:
                columns = row.split('\t')
                total_cells += len(columns)
            
            # Confirm paste operation
            reply = QMessageBox.question(
                self,
                "Confirm Paste",
                f"This will paste {len(rows)} rows with {len(rows[0].split('\\t'))} columns "
                f"({total_cells} total cells) starting at row {start_row + 1}, column {start_col + 1}.\n\n"
                "Any existing data in these cells will be overwritten.\n\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Paste the data
            changes_made = 0
            for i, row in enumerate(rows):
                if start_row + i >= self.table.rowCount():
                    break
                    
                columns = row.split('\t')
                for j, cell_text in enumerate(columns):
                    if start_col + j >= self.table.columnCount():
                        break
                    
                    # Remove quotes if present
                    if cell_text.startswith('"') and cell_text.endswith('"'):
                        cell_text = cell_text[1:-1].replace('""', '"')
                    
                    # Set the cell value
                    target_row = start_row + i
                    target_col = start_col + j
                    
                    item = self.table.item(target_row, target_col)
                    if item:
                        old_value = item.text()
                        if cell_text != old_value:
                            item.setText(cell_text)
                            # Mark as changed
                            self.changed_cells.add((target_row, target_col))
                            item.setBackground(Qt.yellow)
                            changes_made += 1
            
            if changes_made > 0:
                QMessageBox.information(self, "Paste Successful", 
                                      f"Successfully pasted {changes_made} cells!\n\n"
                                      "Click 'Update Layer' to save changes to QGIS.")
                self.status_label.setText(f"Pasted {changes_made} cells - click 'Update Layer' to save")
            else:
                QMessageBox.information(self, "Paste Complete", 
                                      "Data pasted, but no changes were detected.\n\n"
                                      "This might mean the data was identical to existing values.")
                self.status_label.setText("Paste complete - no changes detected")
                
        except Exception as e:
            QMessageBox.critical(self, 'Paste Error', f"Failed to paste data:\n{str(e)}")
            self.status_label.setText(f"Paste error: {str(e)}")
    


class AttributeManagerDialog(QDialog):
    """Main dialog for the Attribute Manager."""

    def __init__(self, parent=None):
        """Initialize the dialog.
        
        :param parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle('Layer Attribute Manager')
        self.setModal(False)
        self.resize(800, 600)
        
        self.init_ui()
        self.refresh_layers()
        self.select_first_layer()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel('Layer Attribute Manager')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Description
        self.desc_label = QLabel('Manage and edit attribute tables for all vector layers in one interface')
        self.desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.desc_label)
        
        # Layer selection
        layer_group = QGroupBox('Layer Selection')
        layer_layout = QHBoxLayout()
        
        layer_layout.addWidget(QLabel('Select Layer:'))
        self.layer_combo = QComboBox()
        self.layer_combo.currentTextChanged.connect(self.on_layer_changed)
        layer_layout.addWidget(self.layer_combo)
        
        self.refresh_btn = QPushButton('Refresh Layers')
        self.refresh_btn.clicked.connect(self.refresh_layers)
        layer_layout.addWidget(self.refresh_btn)
        
        layer_layout.addStretch()
        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)
        
        # Single attribute table widget (replaces tabs)
        self.table_widget = None
        self.placeholder_label = QLabel('Select a layer to view its attribute table...')
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("QLabel { color: #666; font-style: italic; padding: 50px; }")
        layout.addWidget(self.placeholder_label)
        
        # Status bar
        self.status_label = QLabel('Ready')
        layout.addWidget(self.status_label)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)

    def refresh_layers(self):
        """Refresh the layer list and current table data while preserving current selection."""
        try:
            # Remember current selection
            current_selection = self.layer_combo.currentText()
            
            # Temporarily disconnect the signal to prevent triggering on_layer_changed
            self.layer_combo.currentTextChanged.disconnect(self.on_layer_changed)
            
            # Get vector layers
            vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() 
                           if isinstance(layer, QgsVectorLayer)]
            
            # Update layer combo
            self.layer_combo.clear()
            self.layer_combo.addItems([layer.name() for layer in vector_layers])
            
            # Try to restore previous selection
            if current_selection:
                index = self.layer_combo.findText(current_selection)
                if index >= 0:
                    self.layer_combo.setCurrentIndex(index)
                    # Refresh the current table data without recreating the widget
                    if self.table_widget and hasattr(self.table_widget, 'load_data'):
                        self.table_widget.load_data()
                else:
                    # If previous selection is no longer available, select first layer if any
                    if vector_layers:
                        self.layer_combo.setCurrentIndex(0)
            elif vector_layers:
                # If no previous selection, select first layer
                self.layer_combo.setCurrentIndex(0)
            
            # Reconnect the signal
            self.layer_combo.currentTextChanged.connect(self.on_layer_changed)
            
            if vector_layers:
                self.status_label.setText(f'Loaded {len(vector_layers)} vector layers')
            else:
                self.status_label.setText('No vector layers found')
                
        except Exception as e:
            # Make sure to reconnect the signal even if there's an error
            try:
                self.layer_combo.currentTextChanged.connect(self.on_layer_changed)
            except:
                pass
            QMessageBox.critical(self, 'Error Refreshing Layers', f"Error refreshing layers:\n{str(e)}\n\n"
                               f"This might be a compatibility issue with your QGIS version.")
            self.status_label.setText(f"Error refreshing layers: {str(e)}")

    def select_first_layer(self):
        """Select the first available layer if any exist (only on initial load)."""
        try:
            vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() 
                           if isinstance(layer, QgsVectorLayer)]
            
            if vector_layers and self.layer_combo.count() > 0:
                # Select the first layer (index 0, since there's no placeholder)
                self.layer_combo.setCurrentIndex(0)
        except Exception as e:
            # Don't let this break the dialog
            pass

    def on_layer_changed(self, layer_name):
        """Handle layer selection change."""
        if not layer_name:
            # No layer selected, show placeholder
            if self.table_widget:
                self.layout().removeWidget(self.table_widget)
                self.table_widget.setParent(None)
                self.table_widget = None
            
            # Show placeholder
            self.placeholder_label.setVisible(True)
            return
        
        # Find the selected layer
        vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() 
                       if isinstance(layer, QgsVectorLayer)]
        
        selected_layer = None
        for layer in vector_layers:
            if layer.name() == layer_name:
                selected_layer = layer
                break
        
        if selected_layer:
            # Check if we already have a table widget for this layer
            if (self.table_widget and 
                hasattr(self.table_widget, 'layer') and 
                self.table_widget.layer.name() == layer_name):
                # Same layer, just refresh the data
                self.table_widget.load_data()
                return
            
            # Remove current table widget if exists
            if self.table_widget:
                self.layout().removeWidget(self.table_widget)
                self.table_widget.setParent(None)
            
            # Hide placeholder
            self.placeholder_label.setVisible(False)
            
            # Create new table widget for selected layer
            try:
                self.table_widget = AttributeTableWidget(selected_layer)
                # Insert the table widget before the status label
                layout = self.layout()
                layout.insertWidget(layout.count() - 2, self.table_widget)
            except Exception as e:
                QMessageBox.critical(self, 'Error Loading Data', f"Failed to load layer '{layer_name}':\n{str(e)}")
                self.status_label.setText(f"Error loading layer: {str(e)}")

    
