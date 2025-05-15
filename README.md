# MacOS Resource Monitor MCP Server

A Model Context Protocol (MCP) server that identifies resource-intensive processes on macOS across CPU, memory, and network usage.

## Overview

MacOS Resource Monitor is a lightweight MCP server that exposes an MCP endpoint for monitoring system resources. It analyzes CPU, memory, and network usage, and identifies the most resource-intensive processes on your Mac, returning data in a structured JSON format.

## Requirements

- macOS operating system
- Python 3.10+
- MCP server library

## Installation

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

1. Start the MCP server:
   ```bash
   python src/monitor.py
   ```

2. You should see the message:
   ```
   Simple MacOS Resource Monitor MCP server starting...
   Monitoring CPU, Memory, and Network resource usage...
   ```

3. The server will start and expose the MCP endpoint, which can be accessed by an LLM or other client.

### Using the Tool

The server exposes a single tool:

- `get_resource_intensive_processes()`: Returns information about the most resource-intensive processes

When called, this tool will return a JSON object containing information about the top resource consumers in each category (CPU, memory, and network).

### Sample Output

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

## Potential Improvements

Here are some ways you could enhance this monitor:

- Add disk I/O monitoring
- Improve network usage monitoring to include bandwidth
- Add visualization capabilities
- Extend compatibility to other operating systems
