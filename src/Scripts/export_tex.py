import sys
import os
import json
import argparse

import bpy
import bmesh

sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import blenderhelper


def export_obj(scene, obj):
    old_mesh = bpy.data.meshes[obj.data.name]
    mesh = bmesh.new()
    mesh.from_mesh(old_mesh)
    bmesh.ops.triangulate(mesh, faces=mesh.faces)

    out_dict = {
        'uvs':[],  # UV coordinate of each vertex
        'pos':[],  # Local position of each vertex
        'tris':[]  # Groups of 3 indices into the UV/pos arrays used to build faces
    }
    
    uv_lay = mesh.loops.layers.uv.active
    for face in mesh.faces:
        verts = list()
        for loop in face.loops:
            vert = loop.vert
            if uv_lay is not None:
                uv = loop[uv_lay].uv
                out_dict['uvs'].append([uv.x, uv.y])

            out_dict['pos'].append([
                vert.co.x,
                vert.co.y,
                vert.co.z
            ])
            vert_index = len(out_dict['uvs']) - 1
            verts.append(vert_index)
        out_dict['tris'].append(verts)
            
    return out_dict

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help="Output json data file", required=True)

    config = parser.parse_args(args)

    out_dict = {}
    scene = bpy.context.scene
    for obj in scene.objects:
        if obj.layers[1]:
            out_dict[obj.name] = export_obj(scene, obj)
    print("Saving texture data to {}".format(config.filename))
    json.dump(out_dict, open(config.filename, 'w'))

if __name__ == "__main__":
    blenderhelper.run_function_with_args(main)
