# cxxbuilder
## Simple C++ Incremental Build Tool

This is simply a python script that will search your project directory for source files and 
execute the commands set in the config files. The compiler command is run on each source file 
(*.c, *.cpp) to create an object file, and then the linker command is run once at the end to
produce the executable. 

The compiler command is only run if there is no object file with 'last modified' date newer 
than its corresponding source file, or that source file's included header files. 

The config files are split up into a platform independant project config file and and platform dependant config file. 

## Config file format
The format is simply a variable name followed by a list of of values on separate lines. 
```
NAME0:
value0
value1

NAME2:
value3
```
## Project config
Project config specifies project root directory, binary name and path, include files, targets, 
and project specific libraries for each target

In this sample project config, all directories are specified relative to the project build directory, which is 
in the project root. This project targets windows and linux 64bit platforms. 
```
ROOT_DIR:
..

BIN: 
my-program-name

BIN_DIR:
../bin

INCLUDE_DIRS:
../src/include
../dep/glfw/include
../dep/glew/include

TARGETS:
win64
linux64

LIBS:win64
../dep/glfw/win64/glfw3.lib 
../dep/glew/lib/Release/x64/glew32s.lib
opengl32.lib

LIBS:linux64
../dep/glfw/linux64/glfw3.a
../dep/glew/lib/Release/linux64/glew.a
GL
```

## Platform config
The platform specific config shouldn't have to change between projects.
The config you use will be based on which tools you have availlable on your platform.

This config provides the compile and link commands along with any prefixes required for correct syntax
of those tools. There is also a section for libraries required for a platform. 

This sample platform config is for building win64 apps using MSVC
```
TARGET:
win64

INC_PREFIX:
-I

LIB_PREFIX:

BIN_SUFFIX:
.exe

CXXFLAGS:
-std:c++14 -W4 -EHsc -MD

LDFLAGS:
-NODEFAULTLIB:LIBCMT

LIBS:
gdi32.lib
kernel32.lib
user32.lib
shell32.lib

COMPILER:
cl -c {CXXFLAGS} -Fo{OBJ_PATH} {INCLUDE_DIRS} {SRC_PATH}

LINKER:
link -out:{BIN_DIR}/{TARGET}/{BIN}{BIN_SUFFIX} {OBJ_FILES} {LIBS} {LDFLAGS}
```

## {CMD_VARS}
The variables used in the compiler and linker commands are: 
- SRC_PATH: path to a single source file. The compile command is run once per source file found under the project root directory,
- OBJ_PATH: same as SRC_PATH, except the extension is changed to ".o",
- OBJ_FILES: list of all object files found under the root directory after the compile pass,
- others: all others are specified in the config files. 
