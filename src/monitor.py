"""
Simple MacOS Resource Monitor - An MCP server that identifies resource-intensive processes
for CPU, Memory, Disk, and Network usage.
"""
import os
import subprocess
import json
import re
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Simple MacOS Resource Monitor")

# ===== MCP Tool for Process Monitoring =====
@mcp.tool()
def get_resource_intensive_processes() -> str:
    """
    Identify resource-intensive processes on macOS across CPU, memory, disk, and network.

    Returns:
        A string containing information about resource-intensive processes,
        which can be analyzed to provide optimization suggestions.
    """
    try:
        # Get system resource data
        system_data = {
            "cpu_intensive_processes": get_cpu_intensive_processes(),
            "memory_intensive_processes": get_memory_intensive_processes(),
            "network_intensive_processes": get_network_intensive_processes()
        }

        # Format the results as a nice JSON string
        result = json.dumps(system_data, indent=2)
        return result

    except Exception as e:
        return f"Error monitoring system resources: {str(e)}"

def run_command(cmd):
    """Helper function to run a command and return its output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error running command: {str(e)}"

def get_cpu_intensive_processes(limit=5):
    """Get the top CPU-consuming processes using ps command."""
    output = run_command(["ps", "-eo", "pid,%cpu,comm", "-r"])

    lines = output.split('\n')
    processes = []

    # Skip the header line
    for line in lines[1:limit+1]:
        parts = line.split(None, 2)
        if len(parts) >= 3:
            process = {
                'pid': parts[0],
                'cpu_percent': float(parts[1]),
                'command': parts[2]
            }
            processes.append(process)

    return processes

def get_memory_intensive_processes(limit=5):
    """Get the top memory-consuming processes using ps command."""
    output = run_command(["ps", "-eo", "pid,pmem,rss,comm", "-m"])

    lines = output.split('\n')
    processes = []

    # Skip the header line
    for line in lines[1:limit+1]:
        parts = line.split(None, 3)
        if len(parts) >= 4:
            process = {
                'pid': parts[0],
                'memory_percent': float(parts[1]),
                'resident_memory_kb': int(parts[2]),
                'command': parts[3]
            }
            processes.append(process)

    return processes


def get_network_intensive_processes(limit=5):
    """Get processes with highest network activity."""
    try:
        # Try using lsof to get network connections per process
        output = run_command(["lsof", "-i", "-n", "-P"])

        # Count connections by process
        process_counts = {}
        for line in output.split('\n')[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 9:
                process = parts[0]
                process_counts[process] = process_counts.get(process, 0) + 1

        # Sort and get top processes
        sorted_processes = sorted(process_counts.items(), key=lambda x: x[1], reverse=True)

        processes = []
        for i, (process, count) in enumerate(sorted_processes):
            if i >= limit:
                break

            processes.append({
                'command': process,
                'network_connections': count
            })

        return processes
    except Exception as e:
        return [{"error": f"Could not determine network-intensive processes: {str(e)}"}]


# ===== Main Function =====
if __name__ == "__main__":
    print("Simple MacOS Resource Monitor MCP server starting...")
    print("Monitoring CPU, Memory, and Network resource usage...")
    # Run the MCP server (this will block until exit)
    mcp.run()
