"""
Simple MacOS Resource Monitor - An MCP server that identifies resource-intensive processes
for CPU, Memory, and Network usage.
"""
import os
import subprocess
import json
import re
import logging
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Simple MacOS Resource Monitor")

def safe_call(func, error_prefix="Operation failed"):
    """Helper for safe function calls with consistent error format"""
    try:
        return func()
    except Exception as e:
        return {"error": f"{error_prefix}: {str(e)}"}

# ===== MCP Tool for Process Monitoring =====
@mcp.tool()
def get_resource_intensive_processes() -> str:
    """
    Identify resource-intensive processes on macOS across CPU, memory, and network.

    Returns:
        A string containing information about resource-intensive processes,
        which can be analyzed to provide optimization suggestions.
    """
    # Get system resource data with per-category error handling
    system_data = {
        "cpu_intensive_processes": safe_call(get_cpu_intensive_processes, "CPU monitoring failed"),
        "memory_intensive_processes": safe_call(get_memory_intensive_processes, "Memory monitoring failed"),
        "network_intensive_processes": safe_call(get_network_intensive_processes, "Network monitoring failed")
    }

    # Format the results as a nice JSON string
    result = json.dumps(system_data, indent=2)
    return result

@mcp.tool()
def get_processes_by_category(process_type: str, page: int = 1, page_size: int = 10, 
                            sort_by: str = "auto", sort_order: str = "desc") -> str:
    """
    Get all processes filtered by category (cpu, memory, network) with pagination and sorting support.
    
    Args:
        process_type: Type of processes to retrieve ('cpu', 'memory', or 'network')
        page: Page number (starting from 1, default: 1)  
        page_size: Number of processes per page (default: 10, max: 100)
        sort_by: Sort field - 'auto' (default metric), 'pid', 'command', or metric-specific fields
                 CPU: 'auto'/'cpu_percent', 'pid', 'command'
                 Memory: 'auto'/'memory_percent', 'resident_memory_kb', 'pid', 'command'  
                 Network: 'auto'/'network_connections', 'pid', 'command'
        sort_order: Sort direction - 'desc' (default) or 'asc'
    
    Returns:
        JSON string containing paginated and sorted process information for the specified category
    """
    try:
        # Validate inputs
        valid_types = ['cpu', 'memory', 'network']
        if process_type.lower() not in valid_types:
            return json.dumps({
                "error": f"Invalid process_type '{process_type}'. Must be one of: {', '.join(valid_types)}"
            })
        
        if page < 1:
            page = 1
            
        if page_size < 1:
            page_size = 10
        elif page_size > 100:
            page_size = 100
        
        # Validate sort parameters
        sort_order = sort_order.lower()
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
            
        sort_by = sort_by.lower()
        
        # Define valid sort fields for each process type
        valid_sort_fields = {
            'cpu': ['auto', 'cpu_percent', 'pid', 'command'],
            'memory': ['auto', 'memory_percent', 'resident_memory_kb', 'pid', 'command'],
            'network': ['auto', 'network_connections', 'pid', 'command']
        }
        
        process_type = process_type.lower()
        if sort_by not in valid_sort_fields[process_type]:
            return json.dumps({
                "error": f"Invalid sort_by '{sort_by}' for {process_type} processes. Valid options: {', '.join(valid_sort_fields[process_type])}"
            })
        
        # Get all processes for the specified type
        if process_type == 'cpu':
            all_processes = get_all_cpu_processes()
        elif process_type == 'memory':
            all_processes = get_all_memory_processes()
        elif process_type == 'network':
            all_processes = get_all_network_processes()
            
        # Apply custom sorting if not using default
        if sort_by != 'auto':
            all_processes = sort_processes(all_processes, process_type, sort_by, sort_order)
        
        # Calculate pagination
        total_processes = len(all_processes)
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_processes)
        paginated_processes = all_processes[start_index:end_index]
        
        # Calculate pagination metadata
        total_pages = (total_processes + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        # Determine actual sort field used (resolve 'auto')
        actual_sort_by = sort_by
        if sort_by == 'auto':
            sort_field_map = {
                'cpu': 'cpu_percent',
                'memory': 'memory_percent', 
                'network': 'network_connections'
            }
            actual_sort_by = sort_field_map[process_type]
        
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
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error retrieving {process_type} processes: {str(e)}"
        })

@mcp.tool()
def get_system_overview() -> str:
    """
    Get comprehensive system overview with aggregate statistics similar to Activity Monitor.
    Provides CPU, memory, disk, network statistics, and performance analysis to help
    identify bottlenecks and optimization opportunities.
    
    Returns:
        JSON string containing system overview with performance metrics and analysis
    """
    # Get comprehensive system data with per-category error handling
    system_overview = {
        "timestamp": get_current_timestamp(),
        "cpu": safe_call(get_cpu_overview, "CPU overview failed"),
        "memory": safe_call(get_memory_overview, "Memory overview failed"), 
        "disk": safe_call(get_disk_overview, "Disk overview failed"),
        "network": safe_call(get_network_overview, "Network overview failed"),
        "system": safe_call(get_system_info, "System info failed"),
        "performance_analysis": safe_call(analyze_system_performance, "Performance analysis failed")
    }
    
    return json.dumps(system_overview, indent=2)

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

def get_all_cpu_processes():
    """Get all processes sorted by CPU usage."""
    output = run_command(["ps", "-eo", "pid,%cpu,comm", "-r"])
    
    lines = output.split('\n')
    processes = []
    
    # Skip the header line
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            parts = line.split(None, 2)
            if len(parts) >= 3:
                try:
                    process = {
                        'pid': parts[0],
                        'cpu_percent': float(parts[1]),
                        'command': parts[2]
                    }
                    processes.append(process)
                except ValueError:
                    # Skip lines with invalid CPU values
                    continue
    
    return processes

def get_all_memory_processes():
    """Get all processes sorted by memory usage."""
    output = run_command(["ps", "-eo", "pid,pmem,rss,comm", "-m"])
    
    lines = output.split('\n')
    processes = []
    
    # Skip the header line
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            parts = line.split(None, 3)
            if len(parts) >= 4:
                try:
                    process = {
                        'pid': parts[0],
                        'memory_percent': float(parts[1]),
                        'resident_memory_kb': int(parts[2]),
                        'command': parts[3]
                    }
                    processes.append(process)
                except ValueError:
                    # Skip lines with invalid memory values
                    continue
    
    return processes

def get_all_network_processes():
    """Get all processes with network activity sorted by connection count."""
    try:
        # Try using lsof to get network connections per process
        output = run_command(["lsof", "-i", "-n", "-P"])
        
        # Count connections by process and collect PIDs
        process_counts = {}
        process_pids = {}
        
        for line in output.split('\n')[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 9:
                process = parts[0]
                pid = parts[1] if len(parts) > 1 else "unknown"
                
                process_counts[process] = process_counts.get(process, 0) + 1
                if process not in process_pids:
                    process_pids[process] = pid
        
        # Sort and get all processes with network activity
        sorted_processes = sorted(process_counts.items(), key=lambda x: x[1], reverse=True)
        
        processes = []
        for process, count in sorted_processes:
            processes.append({
                'pid': process_pids.get(process, 'unknown'),
                'command': process,
                'network_connections': count
            })
        
        return processes
    except Exception as e:
        return [{"error": f"Could not determine network processes: {str(e)}"}]

def sort_processes(processes, process_type, sort_by, sort_order):
    """Sort processes by the specified field and order."""
    if not processes or 'error' in processes[0]:
        return processes
    
    reverse_order = (sort_order == 'desc')
    
    try:
        if sort_by == 'pid':
            # Convert PID to int for proper numeric sorting
            def pid_key(p):
                try:
                    return int(p['pid'])
                except (ValueError, TypeError):
                    return 0
            return sorted(processes, key=pid_key, reverse=reverse_order)
            
        elif sort_by == 'command':
            return sorted(processes, key=lambda p: p.get('command', '').lower(), reverse=reverse_order)
            
        elif sort_by == 'cpu_percent':
            return sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=reverse_order)
            
        elif sort_by == 'memory_percent':
            return sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=reverse_order)
            
        elif sort_by == 'resident_memory_kb':
            return sorted(processes, key=lambda p: p.get('resident_memory_kb', 0), reverse=reverse_order)
            
        elif sort_by == 'network_connections':
            return sorted(processes, key=lambda p: p.get('network_connections', 0), reverse=reverse_order)
            
        else:
            # Fallback to default sorting if sort_by is not recognized
            return processes
            
    except Exception as e:
        # If sorting fails, return processes unsorted
        logging.warning(f"Sorting failed: {e}")
        return processes

# ===== System Overview Helper Functions =====

def get_current_timestamp():
    """Get current timestamp for system overview."""
    import datetime
    return datetime.datetime.now().isoformat()

def get_cpu_overview():
    """Get comprehensive CPU statistics."""
    try:
        # Get CPU usage from top command
        cpu_output = run_command(["top", "-l", "1", "-n", "0"])
        cpu_info = {}
        
        # Parse CPU usage line and load average from top output
        lines = cpu_output.split('\n')
        for line in lines:
            if 'CPU usage:' in line:
                # Example: CPU usage: 12.34% user, 5.67% sys, 81.99% idle
                try:
                    parts = line.split(':')[1].strip()
                    for part in parts.split(','):
                        part = part.strip()
                        if 'user' in part:
                            cpu_info['user_percent'] = float(part.split('%')[0])
                        elif 'sys' in part:
                            cpu_info['system_percent'] = float(part.split('%')[0]) 
                        elif 'idle' in part:
                            cpu_info['idle_percent'] = float(part.split('%')[0])
                except (ValueError, IndexError) as e:
                    logging.warning(f"Could not parse CPU usage line: {line}. Error: {e}")
                    continue
            elif 'Load Avg:' in line:
                # Example: Load Avg: 7.95, 7.63, 8.14 
                try:
                    load_part = line.split('Load Avg:')[1].strip()
                    load_values = [float(x.strip()) for x in load_part.split(',')]
                    cpu_info['load_average'] = {
                        '1min': load_values[0] if len(load_values) > 0 else 0.0,
                        '5min': load_values[1] if len(load_values) > 1 else 0.0,
                        '15min': load_values[2] if len(load_values) > 2 else 0.0
                    }
                except (ValueError, IndexError) as e:
                    logging.warning(f"Could not parse Load Avg line: {line}. Error: {e}")
        
        # Fallback: Get load averages from uptime if not already parsed from top
        if 'load_average' not in cpu_info:
            try:
                uptime_output = run_command(["uptime"])
                if 'load average' in uptime_output:
                    load_part = uptime_output.split('load average:')[1].strip()
                    load_averages = []
                    for x in load_part.split(','):
                        try:
                            load_averages.append(float(x.strip()))
                        except ValueError:
                            load_averages.append(0.0)
                    cpu_info['load_average'] = {
                        '1min': load_averages[0] if len(load_averages) > 0 else 0.0,
                        '5min': load_averages[1] if len(load_averages) > 1 else 0.0,
                        '15min': load_averages[2] if len(load_averages) > 2 else 0.0
                    }
            except Exception as load_e:
                cpu_info['load_average'] = {'1min': 0.0, '5min': 0.0, '15min': 0.0}
                logging.warning(f"Could not parse load average: {load_e}")
        
        # Get CPU core count
        try:
            cores = run_command(["sysctl", "-n", "hw.ncpu"])
            cpu_info['cores'] = int(cores) if cores.isdigit() else 'unknown'
        except:
            cpu_info['cores'] = 'unknown'
            
        # Calculate total usage
        if 'idle_percent' in cpu_info:
            cpu_info['total_usage_percent'] = round(100 - cpu_info['idle_percent'], 2)
        
        return cpu_info
        
    except Exception as e:
        return {"error": f"Could not get CPU overview: {str(e)}"}

def get_memory_overview():
    """Get comprehensive memory statistics."""
    try:
        # Get memory info from vm_stat
        vm_output = run_command(["vm_stat"])
        memory_info = {}
        
        page_size = 4096  # Default page size on macOS
        
        # Parse vm_stat output
        for line in vm_output.split('\n'):
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value_str = parts[1].strip().rstrip('.')
                    try:
                        value = int(value_str) * page_size  # Convert pages to bytes
                        memory_info[key] = value
                    except ValueError:
                        continue
        
        # Get total physical memory
        try:
            total_mem = run_command(["sysctl", "-n", "hw.memsize"])
            if total_mem.isdigit():
                memory_info['total_physical_memory'] = int(total_mem)
        except:
            pass
        
        # Calculate derived statistics
        if 'pages_free' in memory_info and 'pages_speculative' in memory_info:
            memory_info['free_memory'] = memory_info['pages_free'] + memory_info['pages_speculative']
        
        if 'pages_active' in memory_info and 'pages_inactive' in memory_info and 'pages_wired_down' in memory_info:
            memory_info['used_memory'] = memory_info['pages_active'] + memory_info['pages_inactive'] + memory_info['pages_wired_down']
        
        # Calculate percentages if we have total memory
        if 'total_physical_memory' in memory_info:
            total = memory_info['total_physical_memory']
            if 'used_memory' in memory_info:
                memory_info['used_percent'] = round((memory_info['used_memory'] / total) * 100, 2)
            if 'free_memory' in memory_info:
                memory_info['free_percent'] = round((memory_info['free_memory'] / total) * 100, 2)
        
        # Convert bytes to human readable
        for key in ['total_physical_memory', 'used_memory', 'free_memory']:
            if key in memory_info:
                memory_info[f"{key}_gb"] = round(memory_info[key] / (1024**3), 2)
        
        return memory_info
        
    except Exception as e:
        return {"error": f"Could not get memory overview: {str(e)}"}

def get_disk_overview():
    """Get disk usage statistics."""
    try:
        # Get disk usage from df command
        df_output = run_command(["df", "-h"])
        disk_info = {
            "filesystems": [],
            "summary": {}
        }
        
        lines = df_output.split('\n')[1:]  # Skip header
        total_size = 0
        total_used = 0
        total_available = 0
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 8 and parts[0].startswith('/dev/'):
                filesystem = {
                    "filesystem": parts[0],
                    "size": parts[1],
                    "used": parts[2], 
                    "available": parts[3],
                    "use_percent": parts[4],
                    "mounted_on": parts[8] if len(parts) > 8 else parts[-1]
                }
                
                # Convert to bytes for summary (rough approximation)
                size_str = parts[1]
                used_str = parts[2]
                
                try:
                    if size_str.endswith('Gi'):
                        total_size += float(size_str[:-2]) * 1024**3
                    elif size_str.endswith('Ti'):
                        total_size += float(size_str[:-2]) * 1024**4
                    elif size_str.endswith('G'):
                        total_size += float(size_str[:-1]) * 1024**3
                    elif size_str.endswith('T'):
                        total_size += float(size_str[:-1]) * 1024**4
                except (ValueError, IndexError):
                    pass
                    
                try:
                    if used_str.endswith('Gi'):
                        total_used += float(used_str[:-2]) * 1024**3
                    elif used_str.endswith('Ti'):
                        total_used += float(used_str[:-2]) * 1024**4
                    elif used_str.endswith('G'):
                        total_used += float(used_str[:-1]) * 1024**3
                    elif used_str.endswith('T'):
                        total_used += float(used_str[:-1]) * 1024**4
                except (ValueError, IndexError):
                    pass
                
                disk_info["filesystems"].append(filesystem)
        
        # Calculate summary
        if total_size > 0:
            disk_info["summary"] = {
                "total_size_gb": round(total_size / 1024**3, 2),
                "total_used_gb": round(total_used / 1024**3, 2),
                "total_available_gb": round((total_size - total_used) / 1024**3, 2),
                "overall_usage_percent": round((total_used / total_size) * 100, 2)
            }
        
        return disk_info
        
    except Exception as e:
        return {"error": f"Could not get disk overview: {str(e)}"}

def get_network_overview():
    """Get network statistics and active connections."""
    try:
        network_info = {
            "interfaces": {},
            "connections": {},
            "summary": {}
        }
        
        # Get network interface statistics
        try:
            netstat_output = run_command(["netstat", "-i"])
            lines = netstat_output.split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 10 and not parts[0].startswith('Name'):
                    interface_name = parts[0]
                    network_info["interfaces"][interface_name] = {
                        "packets_in": parts[4],
                        "errors_in": parts[5],
                        "packets_out": parts[7],
                        "errors_out": parts[8],
                        "collisions": parts[9] if len(parts) > 9 else "0"
                    }
        except:
            pass
        
        # Get active network connections count by type
        try:
            netstat_connections = run_command(["netstat", "-an"])
            tcp_count = netstat_connections.count('tcp4') + netstat_connections.count('tcp6')
            udp_count = netstat_connections.count('udp4') + netstat_connections.count('udp6')
            
            network_info["connections"] = {
                "tcp_connections": tcp_count,
                "udp_connections": udp_count,
                "total_connections": tcp_count + udp_count
            }
        except:
            pass
        
        # Get network processes (top network users)
        try:
            network_processes = get_network_intensive_processes(10)
            network_info["top_network_processes"] = network_processes
        except:
            pass
        
        return network_info
        
    except Exception as e:
        return {"error": f"Could not get network overview: {str(e)}"}

def get_system_info():
    """Get general system information."""
    try:
        system_info = {}
        
        # Get system uptime
        try:
            uptime_output = run_command(["uptime"])
            if 'up' in uptime_output:
                system_info['uptime'] = uptime_output.split('up')[1].split(',')[0].strip()
        except:
            pass
        
        # Get macOS version
        try:
            version_output = run_command(["sw_vers", "-productVersion"])
            system_info['macos_version'] = version_output.strip()
        except:
            pass
        
        # Get system load and user count from uptime
        try:
            uptime_output = run_command(["uptime"])
            if 'user' in uptime_output:
                users_part = uptime_output.split('load average')[0]
                if 'user' in users_part:
                    user_count = users_part.split('user')[0].split()[-1]
                    system_info['logged_in_users'] = int(user_count) if user_count.isdigit() else 1
        except:
            pass
        
        # Get total process count
        try:
            process_count = len(get_all_cpu_processes())
            system_info['total_processes'] = process_count
        except:
            pass
        
        return system_info
        
    except Exception as e:
        return {"error": f"Could not get system info: {str(e)}"}

def analyze_system_performance():
    """Analyze system performance and identify potential bottlenecks."""
    try:
        analysis = {
            "status": "unknown",
            "bottlenecks": [],
            "recommendations": [],
            "performance_score": 0
        }
        
        # Get current system metrics for analysis
        cpu_info = get_cpu_overview()
        memory_info = get_memory_overview()
        disk_info = get_disk_overview()
        
        score = 100  # Start with perfect score
        
        # Analyze CPU performance
        if isinstance(cpu_info, dict) and 'total_usage_percent' in cpu_info:
            cpu_usage = cpu_info['total_usage_percent']
            if cpu_usage > 80:
                analysis["bottlenecks"].append("High CPU usage detected")
                analysis["recommendations"].append("Consider closing unnecessary applications or upgrading CPU")
                score -= 25
            elif cpu_usage > 60:
                analysis["recommendations"].append("Monitor CPU-intensive processes")
                score -= 10
        
        # Analyze load average
        if isinstance(cpu_info, dict) and 'load_average' in cpu_info and 'cores' in cpu_info:
            if isinstance(cpu_info['cores'], int):
                load_per_core = cpu_info['load_average']['1min'] / cpu_info['cores']
                if load_per_core > 1.0:
                    analysis["bottlenecks"].append("System load exceeds available CPU cores")
                    analysis["recommendations"].append("Reduce concurrent processes or upgrade hardware")
                    score -= 20
        
        # Analyze memory usage
        if isinstance(memory_info, dict) and 'used_percent' in memory_info:
            memory_usage = memory_info['used_percent']
            if memory_usage > 85:
                analysis["bottlenecks"].append("High memory usage detected")
                analysis["recommendations"].append("Close memory-intensive applications or add more RAM")
                score -= 20
            elif memory_usage > 70:
                analysis["recommendations"].append("Monitor memory usage and consider upgrading RAM")
                score -= 5
        
        # Analyze disk usage
        if isinstance(disk_info, dict) and 'summary' in disk_info:
            disk_usage = disk_info['summary'].get('overall_usage_percent', 0)
            if disk_usage > 90:
                analysis["bottlenecks"].append("Disk space critically low")
                analysis["recommendations"].append("Free up disk space immediately")
                score -= 30
            elif disk_usage > 80:
                analysis["recommendations"].append("Consider cleaning up files or upgrading storage")
                score -= 10
        
        # Determine overall status
        if score >= 80:
            analysis["status"] = "excellent"
        elif score >= 60:
            analysis["status"] = "good"
        elif score >= 40:
            analysis["status"] = "fair"
        else:
            analysis["status"] = "poor"
        
        analysis["performance_score"] = max(0, score)
        
        # Add general recommendations if no specific issues found
        if not analysis["recommendations"]:
            analysis["recommendations"].append("System performance appears optimal")
        
        return analysis
        
    except Exception as e:
        return {"error": f"Could not analyze system performance: {str(e)}"}


# ===== Main Function =====
def main():
    """Main entry point for the MCP server."""
    print("Simple MacOS Resource Monitor MCP server starting...")
    print("Monitoring CPU, Memory, and Network resource usage...")
    # Run the MCP server (this will block until exit)
    mcp.run()

if __name__ == "__main__":
    main()
