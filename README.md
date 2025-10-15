# MacOS Resource Monitor MCP Server
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/Pratyay/mac-monitor-mcp)](https://archestra.ai/mcp-catalog/pratyay__mac-monitor-mcp)

A Model Context Protocol (MCP) server that identifies resource-intensive processes on macOS across CPU, memory, and network usage.

## Overview

MacOS Resource Monitor is a lightweight MCP server that exposes an MCP endpoint for monitoring system resources. It analyzes CPU, memory, and network usage, and identifies the most resource-intensive processes on your Mac, returning data in a structured JSON format.

## Requirements

- macOS operating system
- Python 3.10+
- MCP server library

## Installation

### Option 1: Global Installation (Recommended)

Install the MCP server globally using uv for system-wide access:

```bash
git clone https://github.com/Pratyay/mac-monitor-mcp.git
cd mac-monitor-mcp
uv tool install .
```

Now you can run the server from anywhere:
```bash
mac-monitor
```

### Option 2: Development Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Pratyay/mac-monitor-mcp.git
   cd mac-monitor-mcp
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. Install the required dependencies:
   ```bash
   pip install mcp
   ```

## Usage

### Global Installation
If you installed globally with uv:
```bash
mac-monitor
```

### Development Installation
If you're running from the project directory:
```bash
python src/mac_monitor/monitor.py
```

Or using uv run (from project directory):
```bash
uv run mac-monitor
```

You should see the message:
```
Simple MacOS Resource Monitor MCP server starting...
Monitoring CPU, Memory, and Network resource usage...
```

The server will start and expose the MCP endpoint, which can be accessed by an LLM or other client.

### Available Tools

The server exposes three tools:

#### 1. `get_resource_intensive_processes()`
Returns information about the top 5 most resource-intensive processes in each category (CPU, memory, and network).

#### 2. `get_processes_by_category(process_type, page=1, page_size=10, sort_by="auto", sort_order="desc")`
Returns all processes in a specific category with advanced filtering, pagination, and sorting options.

**Parameters:**
- `process_type`: `"cpu"`, `"memory"`, or `"network"`
- `page`: Page number (starting from 1, default: 1)
- `page_size`: Number of processes per page (default: 10, max: 100)
- `sort_by`: Sort field - `"auto"` (default metric), `"pid"`, `"command"`, or category-specific fields:
  - **CPU**: `"cpu_percent"`, `"pid"`, `"command"`
  - **Memory**: `"memory_percent"`, `"resident_memory_kb"`, `"pid"`, `"command"`
  - **Network**: `"network_connections"`, `"pid"`, `"command"`
- `sort_order`: `"desc"` (default) or `"asc"`

**Example Usage:**
```python
# Get first page of CPU processes (default: sorted by CPU% descending)
get_processes_by_category("cpu")

# Get memory processes sorted by resident memory, highest first
get_processes_by_category("memory", sort_by="resident_memory_kb", sort_order="desc")

# Get network processes sorted by command name A-Z, page 2
get_processes_by_category("network", page=2, sort_by="command", sort_order="asc")

# Get 20 CPU processes per page, sorted by PID ascending
get_processes_by_category("cpu", page_size=20, sort_by="pid", sort_order="asc")
```

#### 3. `get_system_overview()`
Returns comprehensive system overview with aggregate statistics similar to Activity Monitor. Provides CPU, memory, disk, network statistics, and intelligent performance analysis to help identify bottlenecks and optimization opportunities.

**Features:**
 - **CPU Metrics**: Usage percentages, load averages, core count
 - **Memory Analysis**: Total/used/free memory with percentages
 - **Disk Statistics**: Storage usage across all filesystems
 - **Network Overview**: Active connections, interface statistics
 - **Performance Analysis**: Intelligent bottleneck detection and recommendations
 - **System Information**: macOS version, uptime, process count

**Example Usage:**
```python
 get_system_overview()  # Get comprehensive system overview
```

**Use Cases:** 
- System performance monitoring and analysis
- Identifying performance bottlenecks and slowdowns
- Resource usage trending and capacity planning
- Troubleshooting system performance issues
- Getting quick system health overview

## Sample Output   

#### `get_resource_intensive_processes()` Output

```json
{
  "cpu_intensive_processes": [
    {
      "pid": "1234",
      "cpu_percent": 45.2,
      "command": "firefox"
    },
    {
      "pid": "5678",
      "cpu_percent": 32.1,
      "command": "Chrome"
    }
  ],
  "memory_intensive_processes": [
    {
      "pid": "1234",
      "memory_percent": 8.5,
      "resident_memory_kb": 1048576,
      "command": "firefox"
    },
    {
      "pid": "8901",
      "memory_percent": 6.2,
      "resident_memory_kb": 768432,
      "command": "Docker"
    }
  ],
  "network_intensive_processes": [
    {
      "command": "Dropbox",
      "network_connections": 12
    },
    {
      "command": "Spotify",
      "network_connections": 8
    }
  ]
}
```

#### `get_processes_by_category()` Output

```json
{
  "process_type": "cpu",
  "processes": [
    {
      "pid": "1234",
      "cpu_percent": 45.2,
      "command": "firefox"
    },
    {
      "pid": "5678",
      "cpu_percent": 32.1,
      "command": "Chrome"
    }
  ],
  "sorting": {
    "sort_by": "cpu_percent",
    "sort_order": "desc",
    "requested_sort_by": "auto"
  },
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_processes": 156,
    "total_pages": 16,
    "has_next_page": true,
    "has_previous_page": false
  }
}
```

## How It Works

The MacOS Resource Monitor uses built-in macOS command-line utilities:

- `ps`: To identify top CPU and memory consuming processes
- `lsof`: To monitor network connections and identify network-intensive processes

Data is collected when the tool is invoked, providing a real-time snapshot of system resource usage.

## Integration with LLMs

This MCP server is designed to work with Large Language Models (LLMs) that support the Model Context Protocol. The LLM can use the `get_resource_intensive_processes` tool to access system resource information and provide intelligent analysis.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Management Commands

If you installed the server globally with uv:

- **List installed tools:** `uv tool list`
- **Uninstall:** `uv tool uninstall mac-monitor`
- **Upgrade:** `uv tool install --force .` (from project directory)
- **Install from Git:** `uv tool install git+https://github.com/Pratyay/mac-monitor-mcp.git`

## Recent Updates

### Version 0.2.0 (Latest)
- ✅ Added `get_processes_by_category()` tool with pagination and sorting
- ✅ Added comprehensive sorting options (CPU%, memory, PID, command name)
- ✅ Added proper Python packaging with `pyproject.toml`
- ✅ Added global installation support via `uv tool install`
- ✅ Enhanced error handling and input validation
- ✅ Added pagination metadata with navigation information

## Potential Improvements

Here are some ways you could enhance this monitor:

- Add disk I/O monitoring
- Improve network usage monitoring to include bandwidth
- Add visualization capabilities  
- Extend compatibility to other operating systems
- Add process filtering by resource thresholds
- Add historical data tracking and trends
