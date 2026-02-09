import random
import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create the base Humanoid (Bust)
# Head
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(0, 0, 0))
head = bpy.context.active_object
head.name = "Cortana_Head"
head.scale = (0.8, 1.1, 0.9)

# Neck
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0, location=(0, -1.2, 0))
neck = bpy.context.active_object
neck.name = "Cortana_Neck"

# Shoulders
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.8, 0))
torso = bpy.context.active_object
torso.name = "Cortana_Torso"
torso.scale = (1.5, 0.5, 0.6)

# 2. Materials (The "Hologram" Look)
holo_mat = bpy.data.materials.new(name="Cortana_Hologram")
holo_mat.use_nodes = True
nodes = holo_mat.node_tree.nodes
links = holo_mat.node_tree.links

# Clear nodes
for n in nodes: nodes.remove(n)

# Create nodes for a glowing, semi-transparent violet
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_mix = nodes.new(type='ShaderNodeMixShader')
node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
node_emission = nodes.new(type='ShaderNodeEmission')
node_fresnel = nodes.new(type='ShaderNodeFresnel')

# Configure Emission (Deep Violet)
node_emission.inputs[0].default_value = (0.3, 0.1, 0.8, 1) # Violet
node_emission.inputs[1].default_value = 5.0 # Strength

# Link logic: Use Fresnel to make edges glow more than the center
links.new(node_fresnel.outputs[0], node_mix.inputs[0])
links.new(node_transparent.outputs[0], node_mix.inputs[1])
links.new(node_emission.outputs[0], node_mix.inputs[2])
links.new(node_mix.outputs[0], node_output.inputs[0])

# Assign material
head.data.materials.append(holo_mat)
neck.data.materials.append(holo_mat)
torso.data.materials.append(holo_mat)

# 3. Data-Stream "Hair"
for i in range(15):
    bpy.ops.curve.primitive_bezier_curve_add()
    hair = bpy.context.active_object
    hair.data.bevel_depth = 0.02
    hair.data.materials.append(holo_mat)
    # Randomize hair placement
    hair.location = (0, 1, 0)
    hair.rotation_euler = (math.radians(random.uniform(-30, 30)), 0, math.radians(i * 24))

# 4. Camera and Lighting
bpy.ops.object.camera_add(location=(0, 0, 5), rotation=(math.radians(90), 0, 0))
bpy.context.scene.camera = bpy.context.object

bpy.ops.object.light_add(type='POINT', location=(2, 2, 2))
light = bpy.context.active_object
light.data.energy = 500
light.data.color = (0.5, 0, 1)

# 5. Render Settings
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = "/tmp/cortana_humanoid.png"
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.ops.render.render(write_still=True)
