# MacOS Resource Monitor MCP Server

A Model Context Protocol (MCP) server that identifies resource-intensive processes on macOS and provides performance improvement suggestions.

## Overview

MacOS Resource Monitor is a lightweight MCP server that exposes a REST API endpoint for monitoring system resources. It analyzes CPU and memory usage, identifies the most resource-intensive processes, and provides actionable suggestions to improve your Mac's performance.

## Features

- Identifies top CPU-consuming processes
- Identifies top memory-consuming processes
- Collects system memory statistics
- Monitors disk I/O activity
- Provides intelligent performance improvement suggestions based on:
  - High CPU usage detection
  - High memory usage detection
  - Multiple Chrome instances detection
  - Low system memory warnings
  - General optimization tips

## Requirements

- macOS (tested on macOS Monterey and newer)
- Python 3.7+
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

2. The server will start and expose the MCP endpoint, which can be accessed by an LLM or other client.


## Example Response

```json
{
  "top_cpu_processes": [
    {
      "pid": "1234",
      "cpu": 56.2,
      "memory": 3.4,
      "command": "Google Chrome"
    },
    {
      "pid": "5678",
      "cpu": 23.1,
      "memory": 1.7,
      "command": "Firefox"
    }
  ],
  "top_memory_processes": [
    {
      "pid": "2345",
      "cpu": 12.5,
      "memory": 15.2,
      "command": "Docker"
    }
  ],
  "memory_stats": {
    "Pages free": "12345",
    "Free Memory (MB)": 412.7
  },
  "disk_stats": {
    "kb/t": "32.45",
    "tps": "12.3"
  },
  "suggestions": [
    {
      "type": "cpu",
      "issue": "High CPU usage by Google Chrome (56.2%)",
      "suggestion": "Consider quitting Google Chrome or checking for updates if it's consistently using high CPU."
    },
    {
      "type": "memory",
      "issue": "Multiple Chrome instances detected (4)",
      "suggestion": "Consider using Safari which is more memory-efficient on macOS, or close unused Chrome tabs and extensions."
    }
  ]
}
```

## How It Works

The MacOS Resource Monitor uses standard macOS command-line utilities:

- `ps`: To identify top CPU and memory consuming processes
- `vm_stat`: To gather memory statistics
- `iostat`: To collect disk I/O information

It then analyzes this data to identify potential performance issues and generates meaningful suggestions to improve system performance.

## Integration with LLMs

This MCP server is designed to work with Large Language Models (LLMs) that support the Model Context Protocol. The LLM can use the `get_resource_intensive_processes` tool to access system resource information and provide intelligent analysis and recommendations.

Example LLM conversation:

```
User: My Mac is running slow. Can you check what might be causing it?

LLM: I'll check your system resources.
[Uses get_resource_intensive_processes tool]
I've analyzed your system and found that Google Chrome is using 56.2% of your CPU with multiple instances running. This is likely the main cause of the slowdown. I recommend closing unused Chrome tabs and extensions, or switching to Safari which is more memory-efficient on macOS.
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
