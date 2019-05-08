# face_animator

Renders a model with blendshapes over http using blender.

# Installation
`docker build -t blender_render .`

## Usage
`docker run -it -p5000:5000 blender_render`
Which runs start.sh (edit start.sh to change the location of your fbx model).

To use it:

`http://localhost:5000/info` to see what blendshapes you have available to alter

To render a png send a POST request to `http://localhost:5000` with a json containing parameters from `/info` as the body of the request. If parameters are ommitted the defaults are used instead.

The rotations are in euler xyz format. 
