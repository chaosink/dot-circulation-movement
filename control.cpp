#include <iostream>

// Include GLFW
#include <GLFW/glfw3.h>
extern GLFWwindow* window; // The "extern" keyword here is to access the variable "window" declared in tutorialXXX.cpp. This is a hack to keep the tutorials simple. Please avoid this.
extern float window_ratio;

// Include GLM
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
using namespace glm;

#include "control.hpp"

glm::mat4 ViewMatrix;
glm::mat4 ProjectionMatrix;

glm::mat4 getViewMatrix(){
	return ViewMatrix;
}
glm::mat4 getProjectionMatrix(){
	return ProjectionMatrix;
}

// Initial position : on +Z
const glm::vec3 positionInit = glm::vec3(0, 0, 4.34f);
// Initial horizontal angle : toward -Z
const float horizontalAngleInit = 3.14f;
// Initial vertical angle : none
const float verticalAngleInit = 0.0f;
// Initial Field of View
const float initialFoV = 45.0f;

glm::vec3 position = positionInit;
float horizontalAngle = horizontalAngleInit;
float verticalAngle = verticalAngleInit;

float speed = 5.0f; // 3 units / second
float mouseSpeed = 0.002f;

void computeMatricesFromInputs(){

	// glfwGetTime is called only once, the first time this function is called
	static double lastTime = glfwGetTime();
	static double xpos_last, ypos_last;
	static auto init_mouse_pos = (glfwGetCursorPos(window, &xpos_last, &ypos_last), 0);

	// Compute time difference between current and last frame
	double currentTime = glfwGetTime();
	float deltaTime = float(currentTime - lastTime);

	// Get mouse position
	double xpos, ypos;
	glfwGetCursorPos(window, &xpos, &ypos);

	// Reset mouse position for next frame
//	glfwSetCursorPos(window, 1024/2, 768/2);

	// Compute new orientation
	horizontalAngle += mouseSpeed * float(xpos_last - xpos);
	verticalAngle   += mouseSpeed * float(ypos_last - ypos);
//	std::cout << xpos << " " << ypos << "-----" << xpos_last << " " << ypos_last << "\n";

	// Direction : Spherical coordinates to Cartesian coordinates conversion
	glm::vec3 direction(
		cos(verticalAngle) * sin(horizontalAngle),
		sin(verticalAngle),
		cos(verticalAngle) * cos(horizontalAngle)
	);

	// Right vector
	glm::vec3 right = glm::vec3(
		sin(horizontalAngle - 3.14f/2.0f),
		0,
		cos(horizontalAngle - 3.14f/2.0f)
	);

	// Up vector
	glm::vec3 up = glm::cross(right, direction);

	// Move forward
	if(glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
		position += direction * deltaTime * speed;
	}
	// Move backward
	if(glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
		position -= direction * deltaTime * speed;
	}
	// Strafe right
	if(glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
		position += right * deltaTime * speed;
	}
	// Strafe left
	if(glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
		position -= right * deltaTime * speed;
	}
	if(glfwGetKey(window, GLFW_KEY_PAGE_UP) == GLFW_PRESS) {
		speed += 1;
	}
	if(glfwGetKey(window, GLFW_KEY_PAGE_DOWN) == GLFW_PRESS) {
		speed -= 1;
	}
	if(glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
		position = positionInit;
		horizontalAngle = horizontalAngleInit;
		verticalAngle = verticalAngleInit;
	}

	float FoV = initialFoV;// - 5 * glfwGetMouseWheel(); // Now GLFW 3 requires setting up a callback for this. It's a bit too complicated for this beginner's tutorial, so it's disabled instead.

	// Projection matrix : 45° Field of View, 4:3 ratio, display range : 0.1 unit <-> 100 units
	ProjectionMatrix = glm::perspective(FoV, window_ratio, 0.1f, 100.0f);
	// Camera matrix
	ViewMatrix       = glm::lookAt(
								position,           // Camera is here
								position+direction, // and looks here : at the same position, plus "direction"
								up                  // Head is up (set to 0,-1,0 to look upside-down)
						  );

	// For the next frame, the "last time" will be "now"
	lastTime = currentTime;
	xpos_last = xpos;
	ypos_last = ypos;
}
