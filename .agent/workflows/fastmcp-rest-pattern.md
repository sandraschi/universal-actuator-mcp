---
description: FastMCP 3.1 - Proactive REST Stabilization Pattern
---

# FastMCP 3.1 REST Stabilization

Use this workflow to correctly integrate custom REST endpoints into a FastMCP server while maintaining compatibility with the Starlette/FastAPI-based transport layer.

## 1. Route Registration (server.py)

**Prohibited**: `@app.get` or `@mcp.app.get` (attribute regression risk).
**Pattern**: Use the official `@mcp.custom_route` decorator.

```python
from starlette.responses import JSONResponse

@mcp.custom_route("/api/v1/health", methods=["GET"])
async def health(request):
    """
    Standard Starlette handler signature:
    - Must accept 'request' (even if unused)
    - Must return a Starlette Response object (e.g., JSONResponse)
    """
    return JSONResponse({"status": "ok", "version": "2.0.0"})
```

## 2. Uvicorn Configuration (start.ps1)

When using custom routes, uvicorn must use the **factory pattern** to ensure the ASGI application is correctly built by FastMCP at runtime.

**Pattern**: `uvicorn <module>:<fastmcp_instance>.http_app --factory`

```powershell
uvicorn universal_actuator_mcp.server:mcp.http_app --factory --port 10745
```

## 3. Heuristics

1.  **Transport Consistency**: Custom routes are served over the same transport (HTTP/SSE) as the MCP protocol.
2.  **Signature Compliance**: Always wrap plain dictionaries in `JSONResponse` to avoid Starlette type-hinting failures.
