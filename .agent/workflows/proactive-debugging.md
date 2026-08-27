---
description: FastMCP - Proactive Debugging Heuristic
---

# Proactive Debugging Workflow

Use this workflow to ensure backend stability for the FastMCP gateway without burdening the USER with intermediate tracebacks.

## 1. Loop: Synchronous Stabilization

When applying functional or structural changes to the FastMCP server, follow this loop:

1.  **Apply Logic**: Modify `server.py` or dependencies.
2.  **Run Sync**: Start the uvicorn server in a synchronous command with high `WaitMsBeforeAsync`.
    ```bash
    uv run uvicorn universal_actuator_mcp.server:mcp.http_app --factory --port 10929
    ```
3.  **Monitor StdErr**: Use `WaitMsBeforeAsync: 5000` to capture any initialization tracebacks.
4.  **Resolve & Repeat**: If a `Traceback` is detected, read the exact error and re-apply a fix **before** informing the user.

## 2. Heuristics

1.  **Wait Duration**: 5 seconds is standard for local FastMCP boot times.
2.  **Health Check**: Even if startup succeeds, verify the REST endpoint with a second command (`Invoke-RestMethod`) to confirm route registration.
3.  **Terminal Cleanup**: Always terminate the background test process after verification.

## 3. Objective

Minimize "tedious" turns for the USER. Do not report success until the backend is empirically verified over its intended transport.

