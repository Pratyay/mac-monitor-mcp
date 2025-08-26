# MacOS Resource Monitor MCP - Claude Code Development Guide

## Project Configuration

This project uses the following tools and configurations optimized for Claude Code development:

- **Package Manager**: `uv` (for fast dependency management and global installation)
- **Framework**: FastMCP (for rapid MCP server development)
- **Structure**: Standard Python package layout with `src/` directory
- **Installation**: Global tool installation via `uv tool install`

## Development Workflow

### Initial Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd mac-monitor-mcp
   ```

2. **Install for Development**:
   ```bash
   # For global installation
   uv tool install .
   
   # For local development
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. **Test Installation**:
   ```bash
   # Test global command
   mac-monitor --help 2>&1 || echo "Server starts (no help option)"
   
   # Test local development
   python src/mac_monitor/monitor.py
   ```

### Development Commands

```bash
# Run server locally (development)
python src/mac_monitor/monitor.py

# Run server globally (after installation)
mac-monitor

# Install/update global tool
uv tool install --force .

# Test imports and basic functionality
python -c "from mac_monitor.monitor import main; print('Import successful')"
```

## Code Architecture

### Project Structure
```
mac-monitor-mcp/
├── src/mac_monitor/           # Main package
│   ├── __init__.py           # Package initialization
│   └── monitor.py            # MCP server implementation
├── pyproject.toml            # Package configuration
├── README.md                 # User documentation
├── CLAUDE.md                 # Development guide (this file)
└── IMPLEMENTATION_STATUS.md  # Implementation tracking
```

### Key Components

#### 1. MCP Server (`monitor.py`)
- **Framework**: FastMCP for rapid development
- **Tools**: Two main tools exposed via MCP protocol
- **Architecture**: Functional approach with helper functions

#### 2. Tool Functions
```python
# Tool 1: Quick overview (top 5 per category)
@mcp.tool()
def get_resource_intensive_processes() -> str

# Tool 2: Advanced querying with pagination and sorting
@mcp.tool()
def get_processes_by_category(process_type: str, page: int = 1, 
                            page_size: int = 10, sort_by: str = "auto", 
                            sort_order: str = "desc") -> str
```

#### 3. Helper Functions
- `get_all_cpu_processes()` - CPU monitoring via `ps` command
- `get_all_memory_processes()` - Memory monitoring via `ps` command  
- `get_all_network_processes()` - Network monitoring via `lsof` command
- `sort_processes()` - Flexible sorting system
- `run_command()` - Safe command execution wrapper

## Best Practices Established

### 1. Parameter Validation
Always validate input parameters with helpful error messages:
```python
# Example validation pattern
valid_types = ['cpu', 'memory', 'network']
if process_type.lower() not in valid_types:
    return json.dumps({
        "error": f"Invalid process_type '{process_type}'. Must be one of: {', '.join(valid_types)}"
    })
```

### 2. Error Handling
Wrap system commands and provide meaningful error responses:
```python
try:
    # System command execution
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.stdout.strip()
except Exception as e:
    return f"Error running command: {str(e)}"
```

### 3. JSON Response Structure
Consistent JSON structure with metadata:
```python
result = {
    "process_type": process_type,
    "processes": paginated_processes,
    "sorting": {
        "sort_by": actual_sort_by,
        "sort_order": sort_order,
        "requested_sort_by": sort_by
    },
    "pagination": {
        "current_page": page,
        "page_size": page_size,
        "total_processes": total_processes,
        "total_pages": total_pages,
        "has_next_page": has_next,
        "has_previous_page": has_previous
    }
}
```

### 4. Package Configuration (`pyproject.toml`)
Proper entry point configuration:
```toml
[project.scripts]
mac-monitor = "mac_monitor.monitor:main"
```

## Testing Procedures

### Manual Testing Commands
```bash
# Test basic functionality
python -c "
from mac_monitor.monitor import get_processes_by_category
result = get_processes_by_category('cpu', page=1, page_size=3)
print('Success:', 'processes' in result)
"

# Test sorting functionality
python -c "
from mac_monitor.monitor import get_processes_by_category
import json
result = get_processes_by_category('cpu', sort_by='pid', sort_order='asc')
data = json.loads(result)
print('Sorting test:', data.get('sorting', {}))
"

# Test global installation
mac-monitor --version 2>&1 || echo "Global command available"
```

### Validation Checklist
- [ ] All tools can be imported successfully
- [ ] MCP server starts without errors  
- [ ] Both tools respond to valid parameters
- [ ] Error handling works for invalid inputs
- [ ] Sorting works for all supported fields
- [ ] Pagination calculates correctly
- [ ] Global installation works from any directory

## Troubleshooting Guide

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print('\\n'.join(sys.path))"
   
   # Check package installation
   uv pip list | grep mac-monitor
   ```

2. **Global Command Not Found**
   ```bash
   # Check uv tool installation
   uv tool list
   
   # Reinstall global tool
   uv tool uninstall mac-monitor
   uv tool install .
   ```

3. **Permission Issues with System Commands**
   ```bash
   # Test system commands directly
   ps -eo pid,%cpu,comm -r | head -5
   lsof -i -n -P | head -5
   ```

4. **MCP Server Won't Start**
   ```bash
   # Check dependencies
   python -c "import mcp; print('MCP available')"
   
   # Test basic server import
   python -c "from mac_monitor.monitor import mcp; print('Server config OK')"
   ```

### Performance Considerations

1. **Large Process Lists**: Pagination helps manage memory usage
2. **Command Timeouts**: 10-second timeout prevents hanging
3. **Sorting Performance**: Efficient for typical process counts (<2000)
4. **Memory Usage**: Minimal due to streaming approach

## Deployment Considerations

### Global Installation
- Preferred method for production use
- Uses uv's global tool management
- Available system-wide via `mac-monitor` command
- Easy to upgrade with `uv tool install --force .`

### Development Installation  
- Use for active development
- Allows immediate testing of changes
- Virtual environment isolation

## Extension Guidelines

### Adding New Tools
1. Create new `@mcp.tool()` decorated function
2. Follow existing parameter validation patterns
3. Use consistent JSON response structure
4. Add comprehensive error handling
5. Update documentation in README.md

### Adding New Process Types
1. Extend `valid_types` list in validation
2. Create new helper function (e.g., `get_all_disk_processes()`)
3. Add sorting support in `sort_processes()` function
4. Update documentation with new fields

### Cross-Platform Support
1. Abstract system command execution
2. Create platform-specific command mappings
3. Test thoroughly on each target platform
4. Update requirements and documentation

## Known Limitations

1. **macOS Only**: Currently relies on macOS-specific commands
2. **Network Monitoring**: Limited to connection counts, not bandwidth
3. **Process Details**: Basic information only (PID, CPU%, memory, command)
4. **Real-time Updates**: Static snapshots, no streaming updates

## Recommended IDE Settings

### VS Code Configuration
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "*.toml": "toml"
    }
}
```

## Version History

- **v0.1.0**: Initial MCP server with basic process monitoring
- **v0.2.0**: Added pagination, sorting, and global installation support

## Future Development Notes

- Consider using `psutil` library for cross-platform compatibility
- Implement caching for frequently accessed process information  
- Add configuration file support for customizing monitoring behavior
- Consider WebSocket support for real-time process monitoring