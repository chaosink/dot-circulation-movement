#version 330 core

layout(location = 0) in vec4 vertexPosition_modelspace;
layout(location = 1) in vec4 vertexPosition_modelspace_d;

out VertexData {
	vec4 color;
	vec2 uv;
} vertexOut;

uniform mat4 MVP;

void main() {
	gl_Position = vertexPosition_modelspace;
	vertexOut.color = vertexPosition_modelspace_d;
}
