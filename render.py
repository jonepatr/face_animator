import argparse
import tempfile
from collections import defaultdict
from math import radians

import numpy as np

import bpy
import mathutils
from flask import Flask, request, send_file

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--python")
parser.add_argument("--model", default="model/model.fbx")
parser.add_argument("-b", action="store_true")
parser.add_argument("-noaudio", action="store_true")


args = parser.parse_args()


bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
lamp = bpy.data.objects["Lamp"]
lamp.location = (0.0, -6.25925, 0)

camera = bpy.data.objects["Camera"]
camera.location = (0.0, -10.25925, 0)
camera.rotation_euler = [radians(a) for a in (90, 0.0, 0)]

bpy.ops.import_scene.fbx(filepath=args.model)


for material in bpy.data.materials:
    material.raytrace_mirror.use = False

blendshapes = defaultdict(list)
for key, shape_key in bpy.data.shape_keys.items():
    for name, key_block in shape_key.key_blocks.items():
        blendshapes[name].append(key_block)


@app.route("/info")
def info():
    return ", ".join(blendshapes.keys())


def render(data):
    for key, shape_key in bpy.data.shape_keys.items():
        for name, key_block in shape_key.key_blocks.items():
            key_block.value = float(data.get(name, 0.0))

    if data.get("rotation"):
        rotations = data.get("rotation").split(",")
        print(rotations)
        rotation_type, rotation_values = (
            rotations[0],
            np.array(rotations[1:], dtype=float),
        )

        if rotation_type == "euler_xyz":
            rotation = mathutils.Euler(rotation_values, "XYZ").to_quaternion()
        elif rotation_type == "quaternion_wxyz":
            rotation = rotation_values
        elif rotation_type == "transformation_matrix":
            rotation = mathutils.Matrix(rotation_values.reshape(4, 4)).to_quaternion()
        bpy.data.objects["jointShouldersMiddle"].pose.bones[
            "jointNeck"
        ].rotation_quaternion = rotation

    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        bpy.context.scene.render.filepath = f.name
        bpy.ops.render.render(write_still=True)
        return send_file(f.name, mimetype="image/gif")


@app.route("/")
def render_get():
    return render(request.args.to_dict())


@app.route("/", methods=["POST"])
def render_post():
    try:
        return render(request.get_json(force=True))
    except:
        return "Couldn't parse request."


app.run("0.0.0.0")
