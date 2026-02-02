---
name: blender-mcp
description: Control Blender via Model Context Protocol (MCP). Enables prompt-assisted 3D modeling, scene creation, and manipulation.
metadata: {"clawdbot":{"emoji":"🧊","requires":{"bins":["blender","uvx"],"env":["BLENDER_HOST","BLENDER_PORT"]}}}
---

# Blender MCP

This skill integrates the [blender-mcp](https://github.com/ahujasid/blender-mcp) project, allowing for direct control of Blender.

## Setup

1. **Install the Addon in Blender**:
   - The addon script is located at `{baseDir}/scripts/addon.py`.
   - In Blender: Edit > Preferences > Add-ons > Install... > Select `addon.py`.
   - Enable "Interface: Blender MCP".
   - In the 3D View sidebar (N-panel), find the "BlenderMCP" tab and click "Connect to Claude".

2. **Configure the Environment**:
   - Default host: `localhost`
   - Default port: `9876`

3. **Usage**:
   - Spawns the MCP server using `uvx blender-mcp`.
   - Allows creating, modifying, and deleting objects, material control, and running arbitrary Python code.

## Key Environment Variables
- `BLENDER_HOST`: Defaults to `localhost`.
- `BLENDER_PORT`: Defaults to `9876`.
- `DISABLE_TELEMETRY`: Set to `true` to disable telemetry.
