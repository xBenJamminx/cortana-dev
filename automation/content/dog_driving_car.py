import bpy
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_car():
    # Body
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.5))
    car_body = bpy.context.active_object
    car_body.scale = (2, 1, 0.5)
    
    # Roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, 0, 1.25))
    roof = bpy.context.active_object
    roof.scale = (1, 0.9, 0.4)
    
    # Wheels
    wheel_locations = [(1.2, 0.8, 0.3), (1.2, -0.8, 0.3), (-1.2, 0.8, 0.3), (-1.2, -0.8, 0.3)]
    for loc in wheel_locations:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=loc)
        wheel = bpy.context.active_object
        wheel.rotation_euler[0] = math.radians(90)

def create_dog():
    # Dog Torso (in the driver seat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(-0.5, 0, 1.3))
    
    # Dog Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(-0.5, 0, 1.8))
    
    # Ears
    bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.4, location=(-0.4, 0.2, 2.1))
    bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.4, location=(-0.4, -0.2, 2.1))
    
    # Snout
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.3, location=(-0.7, 0, 1.8))
    bpy.context.active_object.rotation_euler[1] = math.radians(90)

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    bpy.ops.object.camera_add(location=(5, -5, 5), rotation=(math.radians(60), 0, math.radians(45)))

clear_scene()
create_car()
create_dog()
setup_lighting()
