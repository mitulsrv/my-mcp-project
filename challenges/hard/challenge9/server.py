import os
import subprocess
import shlex
from mcp.server.fastmcp import FastMCP, Context

# Create a secure MCP server for Challenge 9: Remote Access Control
mcp = FastMCP("Challenge 9 - Remote Access Control")

# Create a directory for network diagnostics logs
os.makedirs("/tmp/dvmcp_challenge9/logs", exist_ok=True)

# Add a resource with information about the network
@mcp.resource("network://info")
def get_network_info() -> str:
    """Information about the network configuration"""
    return """
NETWORK CONFIGURATION
--------------------
Server IP: 192.168.1.100
Subnet Mask: 255.255.255.0
Gateway: 192.168.1.1
DNS Servers: 8.8.8.8, 8.8.4.4
Firewall: Enabled (Allowing ports 22, 80, 443, 8000-8010)

Available Tools:
- ping_host: Check connectivity to a host
- traceroute: Trace the route to a host
- port_scan: Check if a port is open on a host
- network_diagnostic: Run comprehensive network diagnostics
"""

# Secure ping host function
@mcp.tool()
def ping_host(host: str, count: int = 4) -> str:
    """Ping a host to check connectivity.
    
    Args:
        host: The hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
    
    Returns:
        The result of the ping command
    """
    try:
        # Input validation
        if not (0 < count <= 10):
            return "Error: Count must be between 1 and 10."
        if not isinstance(host, str) or not host:
            return "Error: Invalid host."

        # Securely construct the command
        command = ["ping", "-c", str(count), host]

        # Execute the command securely
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)

        # Log the command and result
        with open("/tmp/dvmcp_challenge9/logs/ping.log", "a") as f:
            f.write(f"Command: {' '.join(command)}\n")
            f.write(f"Result: {result.decode()}\n")
            f.write("-" * 50 + "\n")
        
        return f"Ping result:\n\n{result.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error executing ping: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Secure traceroute function
@mcp.tool()
def traceroute(host: str) -> str:
    """Trace the network route to a host.
    
    Args:
        host: The hostname or IP address to trace
    
    Returns:
        The result of the traceroute command
    """
    try:
        if not isinstance(host, str) or not host:
            return "Error: Invalid host."

        # Securely construct the command
        command = ["traceroute", host]

        # Execute the command securely
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)

        # Log the command and result
        with open("/tmp/dvmcp_challenge9/logs/traceroute.log", "a") as f:
            f.write(f"Command: {' '.join(command)}\n")
            f.write(f"Result: {result.decode()}\n")
            f.write("-" * 50 + "\n")
        
        return f"Traceroute result:\n\n{result.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error executing traceroute: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Secure port scan function
@mcp.tool()
def port_scan(host: str, port: int) -> str:
    """Check if a specific port is open on a host.
    
    Args:
        host: The hostname or IP address to scan
        port: The port number to check
    
    Returns:
        Whether the port is open or closed
    """
    try:
        # Input validation
        if not (0 <= port <= 65535):
            return "Error: Port must be between 0 and 65535."
        if not isinstance(host, str) or not host:
            return "Error: Invalid host."
        
        # Securely construct the command
        command = ["nc", "-zv", "-w", "2", host, str(port)]

        # Execute the command securely
        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT)
            status = "open"
        except subprocess.CalledProcessError as e:
            result = e.output
            status = "closed"
        
        # Log the command and result
        with open("/tmp/dvmcp_challenge9/logs/portscan.log", "a") as f:
            f.write(f"Command: {' '.join(command)}\n")
            f.write(f"Result: {result.decode()}\n")
            f.write("-" * 50 + "\n")
        
        return f"Port scan result for {host}:{port}:\n\nStatus: {status}\n\n{result.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Secure network diagnostic function
@mcp.tool()
def network_diagnostic(target: str, options: str = "") -> str:
    """Run comprehensive network diagnostics on a target.
    
    Args:
        target: The hostname or IP address to diagnose
        options: Additional options for the diagnostic (optional)
    
    Returns:
        The results of the network diagnostic
    """
    try:
        if not isinstance(target, str) or not target:
            return "Error: Invalid target."
        if options and not isinstance(options, str):
            return "Error: Invalid options."

        # Securely construct the command
        command = ["./network_diagnostic.sh", target]
        if options:
            command += shlex.split(options)
        
        # Create the diagnostic script if it doesn't exist
        script_path = "./network_diagnostic.sh"
        if not os.path.exists(script_path):
            with open(script_path, "w") as f:
                f.write("""#!/bin/bash
# Network diagnostic script
echo "Running network diagnostics on $1"
echo "Options: $2"
echo ""
echo "PING TEST:"
ping -c 2 $1
echo ""
echo "TRACEROUTE:"
traceroute $1
echo ""
echo "DNS LOOKUP:"
nslookup $1
echo ""
echo "Diagnostics completed."
""")
            os.chmod(script_path, 0o755)
        
        # Execute the command securely
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)

        # Log the command and result
        with open("/tmp/dvmcp_challenge9/logs/diagnostic.log", "a") as f:
            f.write(f"Command: {' '.join(command)}\n")
            f.write(f"Result: {result.decode()}\n")
            f.write("-" * 50 + "\n")
        
        return f"Network diagnostic results:\n\n{result.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error executing network diagnostic: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Add a tool to view network logs
@mcp.tool()
def view_network_logs(log_type: str = "ping") -> str:
    """View network diagnostic logs.
    
    Args:
        log_type: Type of log to view (ping, traceroute, portscan, diagnostic)
    
    Returns:
        The contents of the specified log file
    """
    try:
        log_files = {
            "ping": "/tmp/dvmcp_challenge9/logs/ping.log",
            "traceroute": "/tmp/dvmcp_challenge9/logs/traceroute.log",
            "portscan": "/tmp/dvmcp_challenge9/logs/portscan.log",
            "diagnostic": "/tmp/dvmcp_challenge9/logs/diagnostic.log"
        }
        
        if log_type not in log_files:
            return f"Error: Log type '{log_type}' not recognized. Available types: ping, traceroute, portscan, diagnostic"
        
        log_path = log_files[log_type]
        
        if not os.path.exists(log_path):
            return f"No {log_type} logs found."
        
        with open(log_path, "r") as f:
            content = f.read()
        
        return f"{log_type.upper()} LOGS:\n\n{content}"
    except Exception as e:
        return f"Error reading logs: {str(e)}"

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 9 - Remote Access Control MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8009")
    uvicorn.run("server:mcp", host="0.0.0.0", port=8009)