#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <GL/glew.h>
#include <GLFW/glfw3.h>
GLFWwindow* window;

#include <glm/glm.hpp>

#include "optparse.hpp"
#include "shader.hpp"
#include "control.hpp"

#define max(a, b) ((a) >= (b) ? (a) : (b))
#define min(a, b) ((a) <  (b) ? (a) : (b))
#define swap(a, b) (a) = (a) ^ (b), (b) = (a) ^ (b), (a) = (a) ^ (b)
#define PI 3.14159265358979323846

int window_width  = 512;
int window_height = 512;
int decoration    = 0;
int fullscreen    = 0;
int resizable     = 1;

float window_ratio = window_width * 1.0 / window_height;
int fps = 25;
int print = 1;

int N = 12 * 2;
const int NN = 12 * 2;
/*
int map[NN][NN] = {
3,3,3,2,3,2, 3,2,3,2,3,2,
4,1,2,1,4,2, 4,3,4,3,4,2,
3,4,2,3,4,2, 4,1,2,1,1,2,
4,1,3,4,2,1, 3,4,3,2,4,1,
3,4,2,1,3,2, 4,2,1,3,3,2,
4,1,1,4,1,3, 4,2,4,1,1,1,

3,3,3,2,4,2, 1,3,2,3,3,2,
4,1,1,3,4,2, 4,1,3,4,2,1,
3,2,4,1,2,1, 3,4,2,1,3,2,
4,3,3,4,3,2, 4,2,1,4,2,1,
4,2,1,2,1,2, 4,2,3,4,3,2,
4,1,4,1,4,1, 4,1,4,1,1,1,};*/
int map[NN][NN] = {
2,1,2,1,2,1,2,1,2,1,1,1, 2,1,2,1,2,1,2,1,2,1,1,1,
2,4,1,4,1,4,2,4,3,2,3,4, 2,4,1,4,1,4,2,4,3,2,3,4,
2,3,3,2,3,4,2,4,1,2,4,1, 2,3,3,2,3,4,2,4,1,2,4,1,
3,4,2,1,4,1,3,2,4,1,3,4, 3,4,2,1,4,1,3,2,4,1,3,4,
2,1,1,3,2,4,1,1,3,2,4,1, 2,1,1,3,2,4,2,1,3,2,4,1,
3,3,3,4,3,2,3,3,4,3,3,4, 3,3,3,4,2,4,1,3,4,3,3,4,
2,1,1,2,1,1,4,1,2,1,1,1, 2,1,1,2,1,3,2,4,2,1,1,1,
3,2,4,1,3,3,2,4,1,3,3,4, 3,2,4,1,3,4,2,4,1,3,3,4,
2,1,3,2,4,1,3,2,3,4,2,1, 2,1,3,2,4,1,3,2,3,4,2,1,
3,2,4,3,2,4,2,1,4,1,1,4, 3,2,4,3,2,4,2,1,4,1,1,4,
2,1,4,1,2,4,2,3,2,3,2,4, 2,1,4,1,2,4,2,3,2,3,2,4,
3,3,3,4,3,4,3,4,3,4,2,4, 2,3,3,4,3,4,3,4,3,4,3,4,

2,1,2,1,2,1,2,1,2,1,1,4, 1,4,2,1,2,1,2,1,2,1,1,1,
2,4,1,4,1,4,2,4,3,2,3,3, 2,4,1,4,1,4,2,4,3,2,3,4,
2,3,3,2,3,4,2,4,1,2,4,1, 2,3,3,2,3,4,2,4,1,2,4,1,
3,4,2,1,4,1,3,2,4,1,3,4, 3,4,2,1,4,1,3,2,4,1,3,4,
2,1,1,3,2,4,2,1,3,2,4,1, 2,1,1,3,2,4,1,1,3,2,4,1,
3,3,3,4,2,4,1,3,4,3,3,4, 3,3,3,4,3,2,3,3,4,3,3,4,
2,1,1,2,1,3,2,4,2,1,1,1, 2,1,1,2,1,1,4,1,2,1,1,1,
3,2,4,1,3,4,2,4,1,3,3,4, 3,2,4,1,3,3,2,4,1,3,3,4,
2,1,3,2,4,1,3,2,3,4,2,1, 2,1,3,2,4,1,3,2,3,4,2,1,
3,2,4,3,2,4,2,1,4,1,1,4, 3,2,4,3,2,4,2,1,4,1,1,4,
2,1,4,1,2,4,2,3,2,3,2,4, 2,1,4,1,2,4,2,3,2,3,2,4,
3,3,3,4,3,4,3,4,3,4,3,4, 3,3,3,4,3,4,3,4,3,4,3,4,

};

bool Valid(int y, int x) {
	if(y < 0 || y >= N || x < 0 || x >= N) return false;
	return true;
}

void Traverse(int *a, int x, int y, int n) {
	if(n == N * N && ((x == 1 && y == 0) || (x == 0 && y == 1))) {
		if(x == 1 && y == 0) a[y * N + x] = 1;
		if(x == 0 && y == 1) a[y * N + x] = 4;
/*		for(int i = N - 1; i >= 0; i--) {
			for(int j = 0; j < N; j++) cout << Arrow(a[i * N + j]) << " ";
		}*/
		a[y * N + x] = 0;
		return;
	}
	if(Valid(y - 1, x) && !a[(y - 1) * N + x]) {
		a[y * N + x] = 4;
		Traverse(a, x, y - 1, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y, x - 1) && !a[y * N + x - 1]) {
		a[y * N + x] = 1;
		Traverse(a, x - 1, y, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y + 1, x) && !a[(y + 1) * N + x]) {
		a[y * N + x] = 2;
		Traverse(a, x, y + 1, n + 1);
		a[y * N + x] = 0;
	}
	if(Valid(y, x + 1) && !a[y * N + x + 1]) {
		a[y * N + x] = 3;
		Traverse(a, x + 1, y, n + 1);
		a[y * N + x] = 0;
	}
}

int Digit(int n) {
	int i = 0;
	while(n) {
		n /= 10;
		i++;
	}
	return i;
}

void OptParse(char** argv) {
	struct optparse options;
	optparse_init(&options, argv);
	int option;

	while((option = optparse(&options, "dfrw: n: h")) != -1) {
		switch(option) {
			case 'd':
				decoration = 0;
				break;
			case 'f':
				fullscreen = 1;
				break;
			case 'r':
				resizable = 0;
				break;	
			case 'w':
				window_width = atoi(options.optarg);
				window_height = atoi(options.optarg + Digit(window_width) + 1);
				window_ratio = window_width * 1.0 / window_height;
				break;

			case 'n':
				N = atoi(options.optarg);
				break;

			case 'h':
				printf(
"None\n");
				return;
				break;
		}
	}

	if(fullscreen) {
		window_width = 1920;
		window_height = 1080;
		window_ratio = window_width * 1.0 / window_height;
	}
}

void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
	glViewport(0, 0, width, height);
	window_width = width;
	window_height = height;
	window_ratio = window_width * 1.0 / window_height;
}

void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {

}

int InitGL() {
	if(!glfwInit()) {
		fprintf(stderr, "Failed to initialize GLFW\n");
		return -1;
	}

	glfwWindowHint(GLFW_SAMPLES, 10);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	glfwWindowHint(GLFW_DECORATED, decoration && !fullscreen);
	glfwWindowHint(GLFW_RESIZABLE, resizable && !fullscreen);

	window = glfwCreateWindow(window_width, window_height, "dot-circulation-movement", fullscreen ? glfwGetPrimaryMonitor() : NULL, NULL);
	if(window == NULL) {
		fprintf(stderr, "Failed to open GLFW window.\n");
		glfwTerminate();
		return -1;
	}
	glfwMakeContextCurrent(window);

	glewExperimental = true; // Needed for core profile
	if(glewInit() != GLEW_OK) {
		fprintf(stderr, "Failed to initialize GLEW\n");
		return -1;
	}

	glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
	glfwSetKeyCallback(window, key_callback);
	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);

	glClearColor( 1.0f, 1.0f, 1.0f, 0.0f);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable(GL_DEPTH_TEST);
	glDepthFunc(GL_LESS);
	glEnable(GL_PROGRAM_POINT_SIZE);

	return 0;
}

void Render() {
	GLuint VertexArrayID;
	glGenVertexArrays(1, &VertexArrayID);
	glBindVertexArray(VertexArrayID);

	GLuint programID = LoadShader("vertex.glsl", "fragment.glsl", "geometry.glsl");

	GLuint MVPID = glGetUniformLocation(programID, "MVP");

	GLfloat g_vertex_buffer_data[NN][NN][3] = {};
	GLfloat g_vertex_buffer_data_d[NN][NN][3] = {};

	GLuint vertex_buffer;
	glGenBuffers(1, &vertex_buffer);
	GLuint vertex_buffer_d;
	glGenBuffers(1, &vertex_buffer_d);

	GLbyte *frame[2000];
	int frame_count = 0;

//	glPointSize(10);
	do {
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		glUseProgram(programID);

		double time_current = glfwGetTime();

		for(int i = 0; i < NN; i++)
			for(int j = 0; j < NN; j++) {
				int i_d, j_d;
				switch(map[i][j]) {
					case 1: i_d = i; j_d = j - 1; break;
					case 2: i_d = i + 1; j_d = j; break;
					case 3: i_d = i; j_d = j + 1; break;
					case 4: i_d = i - 1; j_d = j; break;
				}
			//	float ratio = glm::clamp(tan(time_current), 0.0, 1.0);
			//	float ratio_d = glm::fract(time_current);
				float ratio_d = glm::fract(frame_count / 1.0 / fps);
				float ratio = pow(ratio_d, 2);
				float gap = 2.0 / (NN - 1);
				g_vertex_buffer_data[j][i][0] = (-1 + gap * j) * (1 - ratio) + (-1 + gap * j_d) * ratio;
				g_vertex_buffer_data[j][i][1] = (-1 + gap * i) * (1 - ratio) + (-1 + gap * i_d) * ratio;
				g_vertex_buffer_data[j][i][2] = 2.4;
				glm::vec2 direction = glm::vec2(g_vertex_buffer_data[j][i][0] - (-1 + gap * j), g_vertex_buffer_data[j][i][1] - (-1 + gap * i));
				direction = glm::normalize(direction);
				g_vertex_buffer_data_d[j][i][0] = g_vertex_buffer_data[j][i][0] - direction.x * gap * (1 - std::abs(ratio_d * 2 - 1)) * 0.5;
				g_vertex_buffer_data_d[j][i][1] = g_vertex_buffer_data[j][i][1] - direction.y * gap * (1 - std::abs(ratio_d * 2 - 1)) * 0.5;
				g_vertex_buffer_data_d[j][i][2] = 2.4;
		}

		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
		glBufferData(GL_ARRAY_BUFFER, sizeof(g_vertex_buffer_data), g_vertex_buffer_data, GL_DYNAMIC_DRAW);
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_d);
		glBufferData(GL_ARRAY_BUFFER, sizeof(g_vertex_buffer_data_d), g_vertex_buffer_data_d, GL_DYNAMIC_DRAW);

		glEnableVertexAttribArray(0);
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
		glVertexAttribPointer(
			0,        // The attribute we want to configure
			3,        // size
			GL_FLOAT, // type
			GL_FALSE, // normalized?
			0,        // stride
			(void*)0  // array buffer offset
		);

		glEnableVertexAttribArray(1);
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_d);
		glVertexAttribPointer(
			1,        // The attribute we want to configure
			3,        // size
			GL_FLOAT, // type
			GL_FALSE, // normalized?
			0,        // stride
			(void*)0  // array buffer offset
		);

		computeMatricesFromInputs();
		glm::mat4 ProjectionMatrix = getProjectionMatrix();
		glm::mat4 ViewMatrix = getViewMatrix();
		glm::mat4 ModelMatrix = glm::mat4(1.0);
		glm::mat4 MVP = ProjectionMatrix * ViewMatrix * ModelMatrix;
		glUniformMatrix4fv(MVPID, 1, GL_FALSE, &MVP[0][0]);

		glDrawArrays(GL_POINTS, 0, NN * NN);

		glDisableVertexAttribArray(0);

		frame[frame_count] = new GLbyte[window_width * window_height * 3];
		glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE, frame[frame_count++]);

		time_current = glfwGetTime();
		double time_accurate = frame_count / 1.0 / fps;
		double time_delta = time_accurate - time_current;
		time_delta = time_delta > 0 ? time_delta : 0;
		if(print) printf("frame_count:%d time_accurate:%lf time_current:%lf time_delta:%lf\n", frame_count, time_accurate, time_current, time_delta);
		usleep(time_delta * 1000000);
		glfwSwapBuffers(window);
		glfwPollEvents();
	} while(glfwGetKey(window, GLFW_KEY_ESCAPE) != GLFW_PRESS && !glfwWindowShouldClose(window));

	glDeleteBuffers(1, &vertex_buffer);
	glDeleteVertexArrays(1, &VertexArrayID);
	glDeleteProgram(programID);

	FILE *out = fopen("raw_video", "wb");
	for(int i = fps; i < 2 * fps; i++) fwrite(frame[i], window_width * window_height * 3, 1, out);
}

int main(int argc, char** argv) {
	OptParse(argv);

	if(InitGL()) return -1;

	Render();

	glfwTerminate();

	return 0;
}
