cmake_minimum_required(VERSION 3.10)
project(dot-circulation-movement)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(
    src/thirdparty/glew-2.2.0/include
    src/thirdparty/glfw/include
    src/thirdparty/glm
    ${OPENGL_INCLUDE_DIR}
)

# Define common sources
set(COMMON_SOURCES
    shader.cpp
    optparse.cpp
    control.cpp
)

# Main executable
add_executable(dot-circulation-movement
    dot-circulation-movement.cpp
    ${COMMON_SOURCES}
)

# Link libraries for main executable
target_link_libraries(dot-circulation-movement
    PRIVATE
	glew_s
	glfw
)

# Include directories
target_include_directories(dot-circulation-movement
    PRIVATE
    ${GLEW_INCLUDE_DIRS}
    ${GLFW_INCLUDE_DIRS}
    ${GLM_INCLUDE_DIRS}
)

# Genmap executable
add_executable(genmap genmap.cpp)

# Copy shader files to build directory
file(GLOB SHADERS "*.glsl")
foreach(SHADER ${SHADERS})
    add_custom_command(
        TARGET dot-circulation-movement POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${SHADER}
        $<TARGET_FILE_DIR:dot-circulation-movement>
    )
endforeach()

if(NOT EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty/glew-2.2.0)
	file(DOWNLOAD
		https://github.com/nigels-com/glew/releases/download/glew-2.2.0/glew-2.2.0.zip
		${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty/glew-2.2.0.zip
		STATUS glew_download_status
	)
	list(GET glew_download_status 0 error_code)
	list(GET glew_download_status 1 error_reason)
	if(${error_code} EQUAL 0)
		file(ARCHIVE_EXTRACT
			INPUT "${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty/glew-2.2.0.zip"
			DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty"
		)
	else()
		message(FATAL_ERROR
			"Downloading glew-2.2.0.zip failed because of ${error_reason}!\n"
			"You may try configuring for another time.\n"
			"Or you can download it by yourself from \"https://github.com/nigels-com/glew/releases/download/glew-2.2.0/glew-2.2.0.zip\" and extract to \"src/thirdparty\" so that \"src/thirdparty/glew-2.2.0/build/cmake\" exists."
		)
	endif()
endif()
option(BUILD_UTILS "utilities" OFF)

# Patch GLEW CMakeLists.txt to fix deprecation warning
set(GLEW_CMAKE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty/glew-2.2.0/build/cmake/CMakeLists.txt")
if(EXISTS "${GLEW_CMAKE_PATH}")
    file(READ "${GLEW_CMAKE_PATH}" _glew_cmake_content)
    string(REPLACE "cmake_minimum_required (VERSION 2.8.12)" "cmake_minimum_required (VERSION 3.10)" _glew_cmake_content "${_glew_cmake_content}")
    file(WRITE "${GLEW_CMAKE_PATH}" "${_glew_cmake_content}")
endif()

add_subdirectory(src/thirdparty/glew-2.2.0/build/cmake)

if(NOT EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/src/thirdparty/glfw)
	message(FATAL_ERROR
		"\"src/thirdparty/glfw\" doesn't exist!\n"
		"Did you use \"--recursive\" when cloning?\n"
	)
endif()
option(GLFW_BUILD_EXAMPLES "Build the GLFW example programs" OFF)
option(GLFW_BUILD_TESTS "Build the GLFW test programs" OFF)
option(GLFW_BUILD_DOCS "Build the GLFW documentation" OFF)
option(GLFW_INSTALL "Generate installation target" OFF)
add_subdirectory(src/thirdparty/glfw)
