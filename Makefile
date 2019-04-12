GLFW = `pkg-config --cflags glfw3` `pkg-config --libs --static glfw3`
GLEW = `pkg-config --cflags glew` `pkg-config --libs glew`

INC =
LIB =
COMMON = shader.cpp optparse.cpp control.cpp
TARGET = dot-circulation-movement

all: $(TARGET) genmap

$(TARGET): $(TARGET).cpp $(COMMON)
	clang++ $(TARGET).cpp -o $(TARGET) $(COMMON) $(GLFW) $(GLEW) $(INC) $(LIB)

genmap: genmap.cpp
	clang++ genmap.cpp -o genmap -g
