#version 330 core

layout(points) in;
layout(triangle_strip, max_vertices = 57) out;

in VertexData {
	vec4 color;
	vec2 uv;
} vertexIn[];

out VertexData {
	vec4 color;
	vec2 uv;
} vertexOut;

uniform mat4 MVP;

float PI = 3.14159265358979323846;
int n = 16;
float radius = 0.015;

void main() {
	vec4 direction = gl_in[0].gl_Position - vertexIn[0].color;
	if(direction.y > 0 || abs(direction.x) > 0.00001f) return;

	for(int i = 0; i < n; i++) {
		gl_Position = MVP * gl_in[0].gl_Position;
		EmitVertex();
		gl_Position = MVP * (gl_in[0].gl_Position + radius * vec4(cos(2 * PI / n * i), sin(2 * PI / n * i), 0, 0));
		EmitVertex();
		gl_Position = MVP * (gl_in[0].gl_Position + radius * vec4(cos(2 * PI / n * (i +1)), sin(2 * PI / n * (i + 1)), 0, 0));
		EmitVertex();
		EndPrimitive();
	}

	float len = length(direction);
	direction = normalize(direction);
	vec4 direction_d = direction;
	direction_d.xy = direction_d.yx;
	float gap = vertexIn[0].uv.x;
	float len_d = gap - abs(len * 2 - gap);

	gl_Position = MVP * (vertexIn[0].color - direction * 0);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position + direction_d * radius * 0.5);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position - direction_d * radius * 0.5);
	EmitVertex();
	EndPrimitive();

	gl_Position = MVP * (vertexIn[0].color + direction_d * radius * sin(len * 80) + direction * radius * 0.4);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position + direction_d * radius);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position - direction_d * radius * 0.5);
	EmitVertex();
	EndPrimitive();

	gl_Position = MVP * (vertexIn[0].color - direction_d * radius * sin(len * 80) + direction * radius * 0.2);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position + direction_d * radius * 0.5);
	EmitVertex();
	gl_Position = MVP * (gl_in[0].gl_Position - direction_d * radius);
	EmitVertex();
	EndPrimitive();
}
