'''
This file renders out the layers of a blend file to different names. It is
configured by a JSON file that links a name to visible layers. For example:
[
    {'name':'image_name', 'layers':[2,5]},
]

The json file is provided by the command line arguments. Invoke this script
using:

blender path/to/blendfile.blend --python ./path/to/render_layers.py -- ./path/to/json/file.json ./path/to/output/images

'''
import sys
import os
import json
import argparse

import bpy

sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import blenderhelper


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', help="Output File", required=True)
    parser.add_argument('--opengl', help="Use the OpenGL renderer", action='store_true')
    parser.add_argument('--resolution', help="Resolution Multiplier", default=1.0, type=float)

    config = parser.parse_args(args)

    blenderhelper.render(
        config.filename,
        config.resolution,
        config.opengl
    )


if __name__ == "__main__":
    blenderhelper.run_function_with_args(main)
