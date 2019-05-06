# face_animator

Renders a model with blendshapes over http using blender.

# Installation
`docker build -t blender_render .`

## Usage
`docker run -it -p5000:5000 blender_render`
Which runs start.sh (edit start.sh to change the location of your fbx model).

To use it:

`http://localhost:5000/info` to see what blendshapes you have available to alter

And to render a png send either a GET request using query params for the the blend shapes, such as: `http://localhost:5000?MouthUp=0.9&EyeIn_L=0.1&rotation=euler_xyz,0.4,0.6,0.1` or a POST request to `http://localhost:5000` with a json containing the blendshape as body of the request e.g. `{"MouthUp": 0.9, "EyeIn_L": 0.1, "rotation": "euler_xyz,0.4,0.6,0.1"}`.

The rotation parameter is always available independent of the used model. Currently three methods are supported, `euler_xyz,X,Y,Z`, `quaternion_wxyz,W,X,Y,Z` or `transformation_matrix,a,b,c...p` where a,b,c...p is a flattened 4x4 transformation matrix.
