# Changelog

All notable changes to the MacOS Resource Monitor MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-25

### Added
- **New Tool**: `get_processes_by_category()` with advanced filtering capabilities
- **Pagination Support**: Configurable page size (1-100 processes per page) with complete metadata
- **Comprehensive Sorting System**: 
  - CPU processes: Sort by `cpu_percent`, `pid`, `command`
  - Memory processes: Sort by `memory_percent`, `resident_memory_kb`, `pid`, `command`
  - Network processes: Sort by `network_connections`, `pid`, `command`
  - Support for both ascending (`asc`) and descending (`desc`) sort orders
  - "Auto" sorting mode that defaults to the primary metric for each process type
- **Global Installation Support**: 
  - Added `pyproject.toml` configuration for proper Python packaging
  - Created entry point for system-wide `mac-monitor` command
  - Full compatibility with `uv tool install` for global installation
- **Enhanced Response Structure**: 
  - Added sorting metadata in responses
  - Added pagination navigation information
  - Included total process counts and page calculations
- **Improved Error Handling**: 
  - Comprehensive input validation with helpful error messages
  - Graceful handling of invalid sort fields and parameters
  - Better error reporting for command execution failures

### Changed
- **Project Structure**: Migrated to proper Python package layout with `src/mac_monitor/`
- **Installation Method**: Now supports global installation via `uv tool install .`
- **Main Function**: Added proper entry point function for command-line execution
- **Documentation**: Completely updated README.md with new features and usage examples

### Technical Improvements
- **Performance**: Efficient sorting and pagination for large process lists (tested with 1000+ processes)
- **Memory Management**: Optimized memory usage during large result set processing
- **Code Organization**: Better separation of concerns with dedicated helper functions
- **Type Safety**: Added comprehensive parameter validation and type checking

### Developer Experience
- **Development Workflow**: Added comprehensive development guide in `CLAUDE.md`
- **Implementation Tracking**: Created `IMPLEMENTATION_STATUS.md` for project status tracking
- **Testing**: Improved testing procedures and validation checklist
- **Documentation**: Enhanced inline code documentation and docstrings

## [0.1.0] - Initial Release

### Added
- **Core MCP Server**: FastMCP-based server implementation
- **Primary Tool**: `get_resource_intensive_processes()` returning top 5 processes per category
- **CPU Monitoring**: Process CPU usage monitoring via `ps` command
- **Memory Monitoring**: Process memory usage monitoring via `ps` command  
- **Network Monitoring**: Network connection monitoring via `lsof` command
- **JSON Response Format**: Structured JSON responses for LLM consumption
- **Error Handling**: Basic error handling for command execution failures
- **macOS Compatibility**: Full support for macOS system monitoring

### Technical Implementation
- **System Integration**: Native macOS command-line utilities (`ps`, `lsof`)
- **Command Safety**: Safe command execution with timeout protection
- **Response Structure**: Consistent JSON structure across all tool responses
- **Framework Choice**: FastMCP framework for rapid MCP server development

## Migration Guide

### From v0.1.0 to v0.2.0

**Installation Changes:**
```bash
# Old method (still works for development)
python src/monitor.py

# New global installation method (recommended)
uv tool install .
mac-monitor
```

**Tool Compatibility:**
- `get_resource_intensive_processes()` - **No changes required** (fully backward compatible)
- New tool `get_processes_by_category()` - **Optional enhancement** for advanced use cases

**Response Structure:**
- All existing integrations continue to work unchanged
- New response fields are additive and optional to consume

## Security Notes

### v0.2.0 Security Enhancements
- **Input Validation**: All user inputs are now validated before processing
- **Command Injection Protection**: Enhanced protection against command injection attacks
- **Error Information**: Error messages don't expose system internals
- **Parameter Bounds**: Strict bounds checking on pagination parameters

## Performance Notes

### v0.2.0 Performance Improvements
- **Large Dataset Handling**: Efficient pagination reduces memory usage for large process lists
- **Sorting Optimization**: Optimized sorting algorithms for typical process counts
- **Command Timeouts**: Configurable timeouts prevent hanging operations
- **Memory Usage**: Streaming approach minimizes memory footprint

## Known Issues

### Current Version (v0.2.0)
- **Platform Limitation**: macOS only (Linux/Windows support planned for future release)
- **Network Monitoring**: Limited to connection counts, not bandwidth usage
- **Historical Data**: No historical tracking or trending capabilities

### Resolved Issues
- **Global Installation**: ✅ Resolved in v0.2.0 - Now supports system-wide installation
- **Package Structure**: ✅ Resolved in v0.2.0 - Proper Python package layout
- **Sorting Limitations**: ✅ Resolved in v0.2.0 - Comprehensive sorting system
- **Large Result Sets**: ✅ Resolved in v0.2.0 - Pagination support added

## Future Roadmap

### Planned for v0.3.0
- Cross-platform support (Linux, Windows)
- Disk I/O monitoring capabilities
- Historical data tracking and trends
- Configurable monitoring thresholds

### Planned for v0.4.0
- Real-time bandwidth monitoring
- Process filtering by resource thresholds
- Export functionality (CSV, JSON files)
- Custom monitoring profiles

## Contributors

- **Initial Development**: Implementation of core MCP server and basic monitoring
- **v0.2.0 Enhancements**: Advanced pagination, sorting, and packaging improvements

## Acknowledgments

- **FastMCP Framework**: For enabling rapid MCP server development
- **uv Tool System**: For excellent global package management
- **macOS System Utilities**: `ps` and `lsof` commands for reliable system monitoring