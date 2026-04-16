from fastmcp import FastMCP

mcp = FastMCP("Diagnostic")

print(f"Type of mcp.app: {type(mcp.app)}")
try:
    print(f"Type of mcp.http_app: {type(mcp.http_app)}")
except Exception as e:
    print(f"mcp.http_app error: {e}")

print("\nAttributes of mcp:")
print([attr for attr in dir(mcp) if not attr.startswith("_")])

if hasattr(mcp, "app"):
    print("\nAttributes of mcp.app:")
    print([attr for attr in dir(mcp.app) if not attr.startswith("_")])

if hasattr(mcp, "http_app"):
    print("\nAttributes of mcp.http_app:")
    print([attr for attr in dir(mcp.http_app) if not attr.startswith("_")])
