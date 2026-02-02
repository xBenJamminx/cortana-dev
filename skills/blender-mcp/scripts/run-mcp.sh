#!/bin/bash
export BLENDER_HOST=${BLENDER_HOST:-localhost}
export BLENDER_PORT=${BLENDER_PORT:-9876}
export DISABLE_TELEMETRY=true
uvx blender-mcp
