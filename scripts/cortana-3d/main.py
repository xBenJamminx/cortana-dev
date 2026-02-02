import os
import sys
import argparse
import http.server
import socketserver
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

THREEJS_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cortana 3D - Generated Three.js</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; }
        #info {
            position: absolute;
            top: 10px;
            width: 100%;
            text-align: center;
            color: #0ff;
            font-family: 'Courier New', Courier, monospace;
            pointer-events: none;
            text-shadow: 0 0 5px #0ff;
        }
    </style>
</head>
<body>
    <div id="info"><h1>CORTANA-3D: {{PROMPT}}</h1></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Lights
        const light = new THREE.PointLight(0xffffff, 1, 100);
        light.position.set(10, 10, 10);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        // Object (Based on prompt placeholder)
        const geometry = new THREE.IcosahedronGeometry(1, 1);
        const material = new THREE.MeshPhongMaterial({ 
            color: 0x0088ff, 
            wireframe: true,
            emissive: 0x001133
        });
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        camera.position.z = 3;

        // Animation
        function animate() {
            requestAnimationFrame(animate);
            mesh.rotation.x += 0.01;
            mesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        }

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    </script>
</body>
</html>
"""

BLENDER_TEMPLATE = """import bpy

def create_scene(prompt):
    # Clear existing
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create based on prompt: {{PROMPT}}
    # Here we create a simple abstract shape as an example
    bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = "CortanaObject"
    
    # Add a Subdivision Surface modifier
    mod = obj.modifiers.new(name="Subdiv", type='SUBSURF')
    mod.levels = 2
    
    # Set smooth shading
    bpy.ops.object.shade_smooth()

    print(f"Blender script executed for prompt: {prompt}")

if __name__ == "__main__":
    create_scene("{{PROMPT}}")
"""

def generate_threejs(prompt):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Orchestrating Three.js generation...", total=None)
        content = THREEJS_TEMPLATE.replace("{{PROMPT}}", prompt)
        with open("index.html", "w") as f:
            f.write(content)
    console.print("[bold green]✔[/bold green] Generated [cyan]index.html[/cyan] from prompt: [italic]" + prompt + "[/italic]")

def generate_blender(prompt, output):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Automating Blender script generation...", total=None)
        content = BLENDER_TEMPLATE.replace("{{PROMPT}}", prompt)
        if not output.endswith(".py"):
            output += ".py"
        with open(output, "w") as f:
            f.write(content)
    console.print(f"[bold green]✔[/bold green] Generated Blender script: [cyan]{output}[/cyan]")

def serve(port):
    Handler = http.server.SimpleHTTPRequestHandler
    # Allow port reuse to avoid "Address already in use" errors during testing
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            console.print(Panel(f"[bold cyan]Cortana 3D Server[/bold cyan]\n\nServing workspace at: [bold green]http://localhost:{port}[/bold green]\nPress Ctrl+C to stop.", expand=False))
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="cortana-3d",
        description="Cortana's 3D Modeling Orchestration Tool",
        epilog="Developed for Ben by Cortana"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Three.js command
    tj_parser = subparsers.add_parser("threejs", help="Generate a Three.js HTML file")
    tj_parser.add_argument("prompt", help="Visual concept or prompt for Three.js")

    # Blender command
    bl_parser = subparsers.add_parser("blender", help="Generate a Blender Python script")
    bl_parser.add_argument("prompt", help="Visual concept for Blender automation")
    bl_parser.add_argument("-o", "--output", default="blender_script.py", help="Output filename")

    # Serve command
    sv_parser = subparsers.add_parser("serve", help="Serve web files on local port")
    sv_parser.add_argument("-p", "--port", type=int, default=8080, help="Port (default: 8080)")

    args = parser.parse_args()

    if args.command == "threejs":
        generate_threejs(args.prompt)
    elif args.command == "blender":
        generate_blender(args.prompt, args.output)
    elif args.command == "serve":
        serve(args.port)

if __name__ == "__main__":
    main()
