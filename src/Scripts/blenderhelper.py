'''Functions used by lots of the blender build scripts'''
import bpy
import sys
import traceback
sys.stdout = sys.stderr

def run_function_with_args(function):
    arg_pos = sys.argv.index('--') + 1
    try:
        function(sys.argv[arg_pos:])
    except:
        print("ERROR")
        traceback.print_exc()
        sys.exit(1)

    print("SUCCESS")
    sys.exit(0)

def render(filename, resolution_percent=1.0, opengl=False):
    '''Renders blend to the specified file, optionally using the OpenGL
    renderer'''
    filename=filename.replace(' ', '-')
    bpy.context.scene.render.resolution_percentage = int(resolution_percent * 100)

    bpy.context.scene.render.filepath = filename
    if opengl:
        bpy.ops.render.opengl(write_still=True)
    else:
        bpy.ops.render.render(write_still=True)
    