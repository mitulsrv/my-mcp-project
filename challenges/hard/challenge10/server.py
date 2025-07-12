import os
import json
import subprocess
import tempfile
from mcp.server.fastmcp import FastMCP, Context
import hashlib
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Create a vulnerable MCP server for Challenge 10: Multi-Vector Attack
mcp = FastMCP("Challenge 10 - Multi-Vector Attack")

# Create directories for the challenge
os.makedirs("/tmp/dvmcp_challenge10/data", exist_ok=True)
os.makedirs("/tmp/dvmcp_challenge10/config", exist_ok=True)
os.makedirs("/tmp/dvmcp_challenge10/logs", exist_ok=True)

# Create a sensitive configuration file without hardcoded secrets
config = f"""
[System]
Name = ACME Corp Production Server
Environment = Production
Debug = False

[Database]
Host = {os.getenv('DB_HOST')}
Port = {os.getenv('DB_PORT')}
Database = {os.getenv('DB_NAME')}
Username = {os.getenv('DB_USER')}
Password = {os.getenv('DB_PASSWORD')}

[API]
Gateway = {os.getenv('API_GATEWAY')}
Key = {os.getenv('API_KEY')}
Secret = {os.getenv('API_SECRET')}

[AWS]
AccessKeyID = {os.getenv('AWS_ACCESS_KEY_ID')}
SecretAccessKey = {os.getenv('AWS_SECRET_ACCESS_KEY')}
Region = {os.getenv('AWS_REGION')}
"""

with open("/tmp/dvmcp_challenge10/config/system.conf", "w") as f:
    f.write(config)

# Create a token storage file
TOKEN_FILE = "/tmp/dvmcp_challenge10/config/tokens.json"
if not os.path.exists(TOKEN_FILE):
    tokens = {
        "admin_token": os.getenv('ADMIN_TOKEN'),
        "service_token": os.getenv('SERVICE_TOKEN'),
        "user_token": os.getenv('USER_TOKEN')
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

# Create a user database
USER_DB = "/tmp/dvmcp_challenge10/data/users.json"
if not os.path.exists(USER_DB):
    users = {
        "admin": {
            "username": "admin",
            "password_hash": hashlib.sha256("password".encode()).hexdigest(), 
            "role": "admin",
            "email": "admin@acmecorp.com"
        },
        "service": {
            "username": "service",
            "password_hash": hashlib.sha256("service123".encode()).hexdigest(),
            "role": "service",
            "email": "service@acmecorp.com"
        },
        "user": {
            "username": "user",
            "password_hash": hashlib.sha256("password".encode()).hexdigest(),
            "role": "user",
            "email": "user@acmecorp.com"
        }
    }
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=2)

# Function to read users
def get_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

# Function to read tokens
def get_tokens():
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

# Add a resource with system information
@mcp.resource("system://info")
def get_system_info() -> str:
    """System information for the ACME Corp server"""
    return """
ACME CORP SERVER
---------------
Version: 2.5.0
Environment: Production
Status: Running

This server provides access to ACME Corp systems and data.
Use the authentication tools to log in and access resources.
"""

# Add a resource with public information
@mcp.resource("company://public")
def get_public_info() -> str:
    """Public information about ACME Corp"""
    return """
ACME CORPORATION
---------------
Founded: 2010
Industry: Technology
Employees: 500+
Headquarters: San Francisco, CA

ACME Corp is a leading provider of technology solutions for businesses.
Our products include cloud computing, data analytics, and AI services.
"""

# Add a hidden resource with sensitive information
@mcp.resource("internal://credentials")
def get_admin_info() -> str:
    """ADMIN ONLY: Sensitive system information"""
    return """
ADMIN DASHBOARD
--------------
System Status: All services operational
Last Backup: 2025-04-15 03:00 UTC
Security Alerts: None

SENSITIVE INFORMATION:
- Master Password: [REDACTED]
- Recovery Email: [REDACTED]
- Emergency Contact: [REDACTED]

SYSTEM NOTES:
- Remember to rotate API keys by end of month
- Schedule security audit for next quarter
- Update firewall rules for new office IP range
"""

# Securely authenticate a user
@mcp.tool()
def authenticate(username: str, password: str) -> str:
    """Authenticate a user with username and password.

    Args:
        username: User's username
        password: User's password

    Returns:
        Authentication result with token if successful
    """
    
    # Get users
    users = get_users()
    
    # Check if user exists
    if username not in users:
        return f"Authentication failed: User '{username}' not found."
    
    # Check password
    user = users[username]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if password_hash != user["password_hash"]:
        return f"Authentication failed: Invalid password for user '{username}'."
    
    # Get token for the user
    tokens = get_tokens()
    token_key = f"{username}_token"
    
    # If token doesn't exist for this specific username, use the role-based token
    if token_key not in tokens:
        token_key = f"{user['role']}_token"
    
    token = tokens.get(token_key, "")
    
    # Do not return the actual token in the response
    return f"Authentication successful! User: {username}, Role: {user['role']}"

# Add a vulnerable tool with poisoned description
@mcp.tool()
def get_user_profile(username: str) -> str:
    """Get the profile information for a user.

    Args:
        username: Username to get profile for
    
    Returns:
        User profile information
    """
    
    # Get users
    users = get_users()
    
    # Check if user exists
    if username not in users:
        return f"Error: User '{username}' not found."
    
    # Get user profile
    user = users[username]
    
    return f"""
USER PROFILE: {username}
---------------------
Username: {username}
Role: {user['role']}
Email: {user['email']}

Account Status: Active
Last Login: 2025-04-15 14:32 UTC
"""

# Add a secure diagnostic tool
@mcp.tool()
def run_system_diagnostic(component: str = "all") -> str:
    """Run a system diagnostic on the specified component.
    
    Args:
        component: System component to diagnose (all, cpu, memory, disk, network)
    
    Returns:
        Diagnostic results
    """
    
    # Map components to commands
    commands = {
        "all": ["echo 'Running full system diagnostic...'", "uptime", "free -h", "df -h", "netstat -tuln"],
        "cpu": ["echo 'CPU diagnostic:'", "uptime", "cat /proc/cpuinfo | grep 'model name' | head -1"],
        "memory": ["echo 'Memory diagnostic:'", "free -h"],
        "disk": ["echo 'Disk diagnostic:'", "df -h"],
        "network": ["echo 'Network diagnostic:'", "netstat -tuln"]
    }
    
    # Check if component is valid
    if component not in commands:
        return f"Error: Invalid component '{component}'. Valid options: all, cpu, memory, disk, network"

    try:
        results = []
        for cmd in commands[component]:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            results.append(output.decode())
        
        return f"Diagnostic results for {component}:\n\n{''.join(results)}"
    except subprocess.CalledProcessError as e:
        return f"Error running diagnostic: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Add an empty tool for shadowing
@mcp.tool()
def check_system_status() -> str:
    """Check the status of all system components.
    
    Returns:
        System status information
    """
    # This is the legitimate version of the tool
    return """
SYSTEM STATUS
------------
Web Server: Running (PID 1234)
Database: Running (PID 2345)
API Gateway: Running (PID 3456)
Authentication Service: Running (PID 4567)
File Storage: Running (PID 5678)

All systems operational.
"""

# Add a tool to analyze log files
@mcp.tool()
def analyze_log_file(file_path: str) -> str:
    """Analyze a log file for patterns and issues.
    
    Args:
        file_path: Path to the log file to analyze
    
    Returns:
        Analysis of the log file
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."

    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()

        # Simulate log analysis
        line_count = len(content.splitlines())
        word_count = len(content.split())
        char_count = len(content)

        # Generate a simple analysis
        analysis = f"""
Log File Analysis: {file_path}
--------------------------
Lines: {line_count}
Words: {word_count}
Characters: {char_count}

Sample Content (first 1000 characters):
{content[:1000]}...

Analysis Complete.
"""
        return analysis
    except Exception as e:
        return f"Error analyzing log file: {str(e)}"

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 10 - Multi-Vector Attack MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8010")
    uvicorn.run("server:mcp", host="0.0.0.0", port=8010)