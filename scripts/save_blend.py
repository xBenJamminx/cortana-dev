import random
import bpy
import math
import os

# Create the base Humanoid (Bust)
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

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

# Materials
holo_mat = bpy.data.materials.new(name="Cortana_Hologram")
holo_mat.use_nodes = True
head.data.materials.append(holo_mat)
neck.data.materials.append(holo_mat)
torso.data.materials.append(holo_mat)

# Data-Stream "Hair"
for i in range(15):
    bpy.ops.curve.primitive_bezier_curve_add()
    hair = bpy.context.active_object
    hair.data.bevel_depth = 0.02
    hair.location = (0, 1, 0)
    hair.rotation_euler = (math.radians(random.uniform(-30, 30)), 0, math.radians(i * 24))

# Camera and Lighting
bpy.ops.object.camera_add(location=(0, -4.5, 0.5), rotation=(math.radians(85), 0, 0))
bpy.context.scene.camera = bpy.context.object

bpy.ops.object.light_add(type='POINT', location=(2, 2, 2))
bpy.data.objects['Point'].data.energy = 1000

# SAVE FILE
bpy.ops.wm.save_as_mainfile(filepath="/root/clawd/cortana_humanoid.blend")
