import bpy
import os
import sys
import argparse
import json

sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import blenderhelper

SPAWN_GROUP_NAME = "ShipSpawn"
STARTLINE_GROUP_NAME = "StartLine"


def get_pos(transformation_matrix):
    '''returns the x/y position from a transformation matrix'''
    pos = transformation_matrix.translation
    return [pos.x, pos.y]

def get_rot(transformation_matrix):
    '''returns the z rotation from a transformation matrix'''
    return transformation_matrix.to_euler().z

def represent_empty(obj):
    return {
        "p": get_pos(obj.matrix_world),
        "r": get_rot(obj.matrix_world),
    }

def to_world(obj, co):
    '''Converts a coordinate to world coords'''
    pos = list((obj.matrix_world.inverted() * co).xy)
    return pos
    

def process_curve(out_dict, curve_obj):
    for spline in curve_obj.data.splines:
        if spline.type != 'BEZIER':
            raise Exception("Can only export bezier curves as level geometry")
        points = spline.bezier_points
        for segment_id in range(len(points[:-1])):
            prev_point = points[segment_id]
            next_point = points[segment_id+1]
            out_dict["beziers"].append({
                "p1":to_world(curve_obj, prev_point.co),
                "p2":to_world(curve_obj, prev_point.handle_right),
                "p3":to_world(curve_obj, next_point.handle_left),
                "p4":to_world(curve_obj, next_point.co),
            })
            

def process_empty(out_dict, empty_obj):
    if empty_obj.dupli_group.name == SPAWN_GROUP_NAME:
        out_list = out_dict["spawns"]
        out_list.append(represent_empty(empty_obj))
    elif empty_obj.dupli_group.name == STARTLINE_GROUP_NAME:
        if out_dict["line"] is not None:
            raise Exception("Two start lines detected")
        else:
            out_dict["line"] = represent_empty(empty_obj)
                

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--foldername', help="Output Folder Path", required=True)
    config = parser.parse_args(args)

    out_dict = {
        "spawns":[],
        "line":None,
        "beziers":[]

    }
    all_objs = bpy.context.scene.objects
    alphabetical_objs = sorted(all_objs, key=lambda x:x.name)
    for obj in alphabetical_objs:
        if obj.type == 'CURVE':
            process_curve(out_dict, obj)
        elif obj.type == 'EMPTY':
            process_empty(out_dict, obj)


    if len(out_dict["spawns"]) != 6:
        raise Exception("Need six spawn points")
    if out_dict["line"] is None:
        raise Exception("Need start/finish line")
    print("Exported {} bezier segments".format(len(out_dict["beziers"])))

    level_name = os.path.basename(bpy.data.filepath[:-6])
    if not os.path.exists(config.foldername):
        os.mkdir(config.foldername)
    json.dump(out_dict, open(os.path.join(config.foldername, level_name+'.json'), 'w'))
    

if __name__ == "__main__":
    blenderhelper.run_function_with_args(main)