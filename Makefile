GLFW = `pkg-config --cflags glfw3` `pkg-config --libs --static glfw3`
GLEW = `pkg-config --cflags glew` `pkg-config --libs glew`

INC =
LIB =
COMMON = src/shader.cpp src/optparse.cpp src/control.cpp
TARGET = dot-circulation-movement

all: $(TARGET) genmap

$(TARGET): src/$(TARGET).cpp $(COMMON)
	clang++ src/$(TARGET).cpp -o $(TARGET) $(COMMON) $(GLFW) $(GLEW) $(INC) $(LIB)

genmap: genmap.cpp
	clang++ src/genmap.cpp -o genmap -g
