#version 330 core

out vec4 color;

in VertexData {
	vec4 color;
	vec2 uv;
} vertexIn;

void main() {
	color = vec4( 1, 0, 0, 1);
}
