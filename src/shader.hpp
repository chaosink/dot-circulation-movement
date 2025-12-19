#ifndef SHADER_HPP
#define SHADER_HPP

GLuint LoadShader(const char *vertex_file_path, const char *fragment_file_path, const char *geometry_file_path = NULL);

GLuint LoadShaderFromString(const char *vertex_string, const char *fragment_string, const char *geometry_string = NULL);

#endif
