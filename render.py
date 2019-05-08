import argparse
import tempfile

import bpy
import mathutils
from flask import Flask, jsonify, request, send_file
from flask.json import JSONEncoder

app = Flask(__name__)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, mathutils.Euler) or isinstance(obj, mathutils.Vector):
                return list(obj)
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder

parser = argparse.ArgumentParser()
parser.add_argument("--python")
parser.add_argument("--model", default="model/model.fbx")
parser.add_argument("-b", action="store_true")
parser.add_argument("-noaudio", action="store_true")


args = parser.parse_args()


bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

bpy.ops.import_scene.fbx(filepath=args.model)
lamp = bpy.data.objects["Lamp"]
lamp.location = (0.0, -5, 0)

camera = bpy.data.objects["Camera"]
camera.location = (0.0, -10, 0)
camera.rotation_euler = (1.57, 0.0, 0)

for material in bpy.data.materials:
    material.raytrace_mirror.use = False


def build_master_dict():
    objects = {}
    for name, obj in bpy.data.objects.items():
        objects[name] = {
            "rotation": obj.rotation_euler,
            "location": obj.location,
            "scale": obj.scale,
        }

        if hasattr(obj.data, "shape_keys") and obj.data.shape_keys:
            objects[name]["blendshapes"] = {}
            for blendshape_name, key_block in obj.data.shape_keys.key_blocks.items():
                objects[name]["blendshapes"][blendshape_name] = key_block.value

        if obj.pose:
            objects[name]["bones"] = {}
            for bone_name, bone in obj.pose.bones.items():
                objects[name]["bones"][bone_name] = {
                    "rotation": bone.rotation_euler,
                    "location": bone.location,
                    "scale": bone.scale,
                }
    return objects


all_objects = build_master_dict()


@app.route("/info")
def info():
    return jsonify(all_objects)


def render(data):
    for obj, val in all_objects.copy().items():
        bpy_obj = bpy.data.objects[obj]
        bpy_obj.rotation_euler = data.get(obj, {}).get("rotation", val["rotation"])
        bpy_obj.location = data.get(obj, {}).get("location", val["location"])
        bpy_obj.scale = data.get(obj, {}).get("scale", val["scale"])

        for bone_name, bone_val in val.get("bones", {}).items():
            bone = bpy_obj.pose.bones[bone_name]
            # bone.rotation_mode = "XYZ"

            rot_val = (
                data.get(obj, {})
                .get("bones", {})
                .get(bone_name, {})
                .get("rotation", bone_val["rotation"])
            )
            bone.rotation_quaternion = mathutils.Euler(rot_val, "XYZ").to_quaternion()

            bone.location = (
                data.get(obj, {})
                .get("bones", {})
                .get(bone_name, {})
                .get("location", bone_val["location"])
            )
            bone.scale = (
                data.get(obj, {})
                .get("bones", {})
                .get(bone_name, {})
                .get("scale", bone_val["scale"])
            )

        for blendshape_name, blendshape_val in val.get("blendshapes", {}).items():
            bpy_obj.data.shape_keys.key_blocks[blendshape_name].value = (
                data.get(obj, {})
                .get("blendshapes", {})
                .get(blendshape_name, blendshape_val)
            )

    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        bpy.context.scene.render.filepath = f.name
        bpy.ops.render.render(write_still=True)
        return send_file(f.name, mimetype="image/gif")


@app.route("/", methods=["POST"])
def render_post():
    return render(request.get_json(force=True))


app.run("0.0.0.0")
