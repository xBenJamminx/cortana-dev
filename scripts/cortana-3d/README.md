# Cortana 3D CLI tool

A lightweight CLI tool for orchestrating 3D development workflows.

## Features
- **Three.js Generation**: Quickly generate `index.html` with a Three.js boilerplate inspired by your prompt.
- **Blender Automation**: Generate Python scripts for Blender based on templates.
- **Live Serving**: One-command local server to preview your web-based 3D content.

## Installation
Add the tool to your path or run it directly:
```bash
# Direct run
/root/clawd/scripts/cortana-3d/cortana-3d --help
```

## Usage

### 1. Generate Three.js
Generates an `index.html` file in the current directory.
```bash
./cortana-3d threejs "Neon Cyberpunk Sphere"
```

### 2. Generate Blender Script
Generates a `.py` script for use in Blender's Scripting tab.
```bash
./cortana-3d blender "Abstract Geometric Composition" -o my_script.py
```

### 3. Serve Generated Files
Starts a local server on port 8080.
```bash
./cortana-3d serve
```
Access at: `http://localhost:8080`

## Structure
- `main.py`: Core logic using `rich` for interactivity.
- `cortana-3d`: Executable shell wrapper.
