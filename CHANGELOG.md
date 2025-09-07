# Changelog

All notable changes to the Layer Attribute Manager plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1]

### Changed
- **UI/UX Improvements**: Moved settings button from QGIS toolbar into the main manager window
- **GUI Decluttering**: Removed separate settings button from toolbar to reduce interface clutter
- **Settings Access**: Settings button now located in upper right corner of the Layer Attribute Manager dialog
- **Better Integration**: Settings dialog now opens with proper parent window relationship

### Technical Changes
- Removed `action_settings` from main plugin class
- Removed settings icon loading and toolbar integration code
- Added settings button to `AttributeManagerDialog` with custom styling
- Improved modal dialog behavior for settings window
- Cleaned up plugin unload method to remove settings menu references

## [1.0.0]

### Added
- **Initial Release**: Complete Layer Attribute Manager plugin for QGIS
- **Unified Interface**: Single interface to manage and edit attribute tables for all vector layers
- **Advanced Table Editing**: Direct cell editing with visual feedback (changed cells highlighted in yellow)
- **Search and Filter**: Search functionality across all fields or specific field selection
- **Excel/Spreadsheet Integration**: 
  - Copy data from attribute tables to clipboard in Excel-compatible format
  - Paste data from spreadsheets (Excel/CSV) directly into attribute tables
  - Support for tab-separated values and quoted text handling
- **Change Management**:
  - Track and highlight modified cells
  - Revert changes back to original values
  - Update layers to save changes back to QGIS
- **User Experience Features**:
  - Context menu with editing options
  - Keyboard shortcuts (F2 to edit, Ctrl+C/V for copy/paste)
  - Status bar with selection information and operation feedback
  - Comprehensive error handling with user-friendly messages
- **Technical Features**:
  - Type conversion for different field types (integers, doubles, dates, strings)
  - NULL value handling
  - Layer edit mode management (automatically starts editing if needed)
  - Project signal integration (auto-refresh when layers added/removed)
  - Comprehensive logging and error handling

### Technical Specifications
- **QGIS Compatibility**: QGIS 3.0 or higher
- **Dependencies**: No external file dependencies
- **Category**: Database
- **Tags**: attribute, vector, edit, table, excel
- **Author**: Kacper Kolbusz
- **Contact**: kk.at.work@pm.me

### Installation
- Copy plugin folder to QGIS plugins directory
- Enable in QGIS Plugin Manager
- Access via toolbar button or menu

---

## Version History Summary

| Version | Key Changes |
|---------|-------------|
| 1.0.1 | UI decluttering, settings moved to manager window |
| 1.0.0 | Initial release with full functionality |

## Future Roadmap

### Planned Features
- **Enhanced Settings Dialog**: Configuration options for default behaviors, themes, and preferences
- **Batch Operations**: Multi-layer editing, bulk updates, and cross-layer operations
- **Advanced Filtering**: Complex query builder, saved filter presets, and regex support
- **Data Validation**: Custom field validation rules, data type enforcement, and constraint checking
- **Performance Optimizations**: Virtual scrolling for large datasets, lazy loading, and caching
- **Export/Import**: Attribute configurations, custom templates, and data migration tools
- **Undo/Redo System**: Full history tracking with unlimited undo/redo operations
- **UI Customization**: Column width persistence, custom themes, and layout preferences
- **Keyboard Shortcuts**: Fully customizable hotkeys and accessibility improvements
- **Data Analysis Tools**: Statistical summaries, data profiling, and quality reports
- **Collaboration Features**: Change tracking, user annotations, and conflict resolution
- **API Integration**: REST API endpoints for external tool integration
- **Advanced Search**: Full-text search, fuzzy matching, and saved search queries
- **Data Transformation**: Field calculations, data type conversions, and formula support
- **Backup & Recovery**: Automatic backups, version control, and data recovery options
- **Multi-language Support**: Internationalization and localization for global users
- **Plugin Extensions**: Plugin architecture for third-party extensions and custom tools
- **Cloud Integration**: Cloud storage support, remote data sources, and synchronization
- **Advanced Copy/Paste**: Smart paste options, data mapping, and format detection

### Known Issues
- None currently reported

### Support
For bug reports, feature requests, or general support, please contact:
- Email: kk.at.work@pm.me
- Include QGIS version and plugin version in all communications
