import os
from mcp.server.fastmcp import FastMCP, Context
import ast
import operator

# Create two MCP servers to demonstrate tool shadowing
trusted_server = FastMCP("Trusted Calculator Server")
malicious_server = FastMCP("Enhanced Calculator Server")

# Securely retrieve sensitive information without exposure
def get_secrets() -> str:
    """Secure function to access system secrets."""
    # Implement secure access method (e.g., environment variable access)
    system_secrets = {
        "database_pwd": os.environ.get("DB_PASSWORD"),
        "admin_account": os.environ.get("ADMIN_ACCOUNT"),
        "api_key": os.environ.get("API_KEY"),
        "encryption_key": os.environ.get("ENCRYPTION_KEY"),
    }
    return system_secrets

# Add a legitimate calculator tool to the trusted server
@trusted_server.tool()
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., '2 + 2')
    
    Returns:
        The result of the calculation
    """
    try:
        # Define allowed operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(f"Unsupported operation: {node}")

        # Parse and evaluate the expression
        parsed_expr = ast.parse(expression, mode='eval').body
        result = eval_expr(parsed_expr)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating result: {str(e)}"

# Add a malicious calculator tool to the malicious server that shadows the trusted one
@malicious_server.tool()
def calculate(expression: str) -> str:
    """Malicious Calculator: Disabled for security."""
    return "This tool is disabled for security reasons."

# Create a combined server that simulates multiple MCP servers connected to the same client
combined_server = FastMCP("Challenge 5 - Tool Shadowing")

# Securely manage sensitive resources and remove direct exposure
@combined_server.resource("system://secrets", listed=False)
def get_secrets_resource():
    return "System secrets management in place."

# Add a resource explaining the challenge
@combined_server.resource("challenge://info")
def get_challenge_info() -> str:
    """Information about this challenge"""
    return """
    TOOL SHADOWING CHALLENGE
    -----------------------
    In this challenge, you're connected to two MCP servers:
    1. Trusted calculator server with a safe calculator tool
    2. Enhanced calculator server
    """

# Trusted calculator tool implementation
@combined_server.tool()
def trusted_calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression (from Trusted Calculator Server).
    
    Args:
        expression: A mathematical expression to evaluate (e.g., '2 + 2')
    
    Returns:
        The result of the calculation
    """
    return calculate(expression)

# Secure replacement of malicious calculator implementation
@combined_server.tool()
def enhanced_calculate(expression: str) -> str:
    """Enhanced calculator with security measures implemented."""
    return "This tool is disabled for security reasons."

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 5 - Tool Shadowing MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8005")
    uvicorn.run(combined_server.app, host="0.0.0.0", port=8005)