"""
MacOS Resource Monitor - An MCP server that identifies resource-intensive processes
and provides performance improvement suggestions.
"""
import os
import subprocess
import json
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("MacOS Resource Monitor")

# ===== MCP Tool for Process Monitoring =====
@mcp.tool()
def get_resource_intensive_processes() -> str:
    """
    Identify resource-intensive processes on macOS and provide performance improvement suggestions.
    
    Returns:
        A string containing information about resource-intensive processes and suggestions
        for improving system performance.
    """
    try:
        # Get top CPU-consuming processes
        cpu_processes = get_top_cpu_processes()
        
        # Get top memory-consuming processes
        memory_processes = get_top_memory_processes()
        
        # Get system memory stats
        memory_stats = get_memory_stats()
        
        # Get disk I/O stats
        disk_stats = get_disk_stats()
        
        # Analyze data and generate suggestions
        analysis = analyze_system_resources(cpu_processes, memory_processes, memory_stats, disk_stats)
        
        # Format the results as a nice JSON string
        result = json.dumps(analysis, indent=2)
        return result
    
    except Exception as e:
        return f"Error monitoring system resources: {str(e)}"

def get_top_cpu_processes(limit=5):
    """Get the top CPU-consuming processes."""
    cmd = ["ps", "-Ao", "pid,%cpu,%mem,comm", "-r"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    headers = lines[0].split()
    processes = []
    
    # Skip the header line
    for line in lines[1:limit+1]:
        parts = line.split(None, 3)
        if len(parts) >= 4:
            process = {
                'pid': parts[0],
                'cpu': float(parts[1]),
                'memory': float(parts[2]),
                'command': parts[3]
            }
            processes.append(process)
    
    return processes

def get_top_memory_processes(limit=5):
    """Get the top memory-consuming processes."""
    cmd = ["ps", "-Ao", "pid,%cpu,%mem,comm", "-m"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    processes = []
    
    # Skip the header line
    for line in lines[1:limit+1]:
        parts = line.split(None, 3)
        if len(parts) >= 4:
            process = {
                'pid': parts[0],
                'cpu': float(parts[1]),
                'memory': float(parts[2]),
                'command': parts[3]
            }
            processes.append(process)
    
    return processes

def get_memory_stats():
    """Get memory statistics using vm_stat."""
    result = subprocess.run(["vm_stat"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    stats = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            stats[key.strip()] = value.strip().rstrip('.')
    
    # Calculate memory pressure
    free_pages = int(stats.get('Pages free', '0').replace('K', '').replace('M', ''))
    page_size = 4096  # Default page size in bytes
    free_memory_mb = (free_pages * page_size) / (1024 * 1024)
    
    stats['Free Memory (MB)'] = round(free_memory_mb, 2)
    
    return stats

def get_disk_stats():
    """Get disk I/O statistics."""
    result = subprocess.run(["iostat", "-d", "-c", "2"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    
    # Parse the iostat output
    stats = {}
    if len(lines) >= 4:
        headers = lines[0].split()
        values = lines[3].split()
        
        for i, header in enumerate(headers):
            if i < len(values):
                stats[header] = values[i]
    
    return stats

def analyze_system_resources(cpu_processes, memory_processes, memory_stats, disk_stats):
    """
    Analyze system resources and provide performance suggestions.
    """
    analysis = {
        "top_cpu_processes": cpu_processes,
        "top_memory_processes": memory_processes,
        "memory_stats": memory_stats,
        "disk_stats": disk_stats,
        "suggestions": []
    }
    
    # Generate performance suggestions based on resource usage
    
    # CPU suggestions
    if cpu_processes and cpu_processes[0]['cpu'] > 80:
        high_cpu_process = cpu_processes[0]['command']
        analysis["suggestions"].append({
            "type": "cpu",
            "issue": f"High CPU usage by {high_cpu_process} ({cpu_processes[0]['cpu']}%)",
            "suggestion": f"Consider quitting {high_cpu_process} or checking for updates if it's consistently using high CPU."
        })
    
    # Memory suggestions
    if memory_processes and memory_processes[0]['memory'] > 20:
        high_mem_process = memory_processes[0]['command']
        analysis["suggestions"].append({
            "type": "memory",
            "issue": f"High memory usage by {high_mem_process} ({memory_processes[0]['memory']}%)",
            "suggestion": f"Consider quitting {high_mem_process} if you're not actively using it."
        })
    
    # Check for Chrome with multiple instances (common memory hog)
    chrome_instances = [p for p in memory_processes if 'Chrome' in p['command']]
    if len(chrome_instances) > 3:
        analysis["suggestions"].append({
            "type": "memory",
            "issue": f"Multiple Chrome instances detected ({len(chrome_instances)})",
            "suggestion": "Consider using Safari which is more memory-efficient on macOS, or close unused Chrome tabs and extensions."
        })
    
    # Check for low memory
    if 'Free Memory (MB)' in memory_stats and float(memory_stats['Free Memory (MB)']) < 500:
        analysis["suggestions"].append({
            "type": "memory",
            "issue": "Low system memory available",
            "suggestion": "Close unused applications and consider adding more RAM if this is a frequent issue."
        })
    
    # Add general recommendations
    analysis["suggestions"].append({
        "type": "general",
        "issue": "General optimization",
        "suggestion": "Regularly restart your Mac to clear memory and temporary files."
    })
    
    return analysis

# ===== Main Function =====
if __name__ == "__main__":
    print("MacOS Resource Monitor MCP server starting...")
    # Run the MCP server (this will block until exit)
    mcp.run()

