
"""Builds C/C++ source"""

import os
from subprocess import call

print()

ROOTDIR = ".."
CXX = "cl"
CC = "cl"
LINKER = "link"
INCLUDES = "-I../src/include -I../dep/glfw/include -I../dep/glew/include"
CXXFLAGS = "-c -std:c++14 -EHsc -MD -W4"
LDFLAGS = "-NODEFAULTLIB:LIBCMT"
LIBS = "gdi32.lib kernel32.lib user32.lib shell32.lib opengl32.lib ..\\dep\\glfw\\win64\\glfw3.lib ..\\dep\\glew\\lib\\Release\\x64\\glew32s.lib"
DEBUG = ""
OUT = "-Fo"
BIN = "-out:../bin/program.exe"


def find_path(filename):
    """ find and return the pathname to filename """
    for (path, dirnames, filenames) in os.walk(ROOTDIR):
        if filename in filenames:
            return os.path.join(path, filename)
    return filename


def get_headers(srcpath):
    """ list all included headers in src """
    headerlist = []
    with open(srcpath, 'r') as srcfile:
        lines = srcfile.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#include"):
                headername = line[10:-1].strip()
                headerpath = find_path(headername)
                headerlist.append(headerpath)
    return headerlist

def needs_recompile(srcpath, objpath, deppath):
    """ determine if src file needs recompile """

    #check if obj file exists
    if not os.path.isfile(objpath):
        print("\nBuilding:", srcpath)
        return True

    #check src file modification time
    if os.path.getmtime(srcpath) > os.path.getmtime(objpath):
        print("\nRebuilding:", srcpath)
        return True

    #check header files' modification time
    for headerpath in get_headers(srcpath):
        headerpath = headerpath.rstrip()
        if os.path.isfile(headerpath):
            if os.path.getmtime(headerpath) > os.path.getmtime(objpath):
                print("\nRebuilding:", srcpath)
                return True

    print("Nothing to be done for:", srcpath)
    return False


def compile_src(srcpath, objpath):
    """ compile the source file """
    if srcpath.lower().endswith(".cpp"):
        COMPILE = CXX
    else:
        COMPILE = CC

    cmdstr = COMPILE +" "+ CXXFLAGS +" "+ OUT+objpath +" "+ INCLUDES +" "+ srcpath
    print('\n',cmdstr,'\n')
    cmd = cmdstr.split(' ')
    call(cmd)


objfilelist = []
#compile each c/cpp file under PWD
for (path, dirnames, filenames) in os.walk(ROOTDIR):
    for filename in filenames:
        if filename.lower().endswith(".c") or filename.lower().endswith(".cpp"):
            name, ext = os.path.splitext(filename)

            srcpath = os.path.join(path, filename)
            objpath = os.path.join(path, name) + ".o"
            deppath = os.path.join(path, name) + ".hd"

            objfilelist.append(objpath)

            if needs_recompile(srcpath, objpath, deppath):
                compile_src(srcpath, objpath)

#link all object files
objstr = "" 
for obj in objfilelist:
    objstr += obj + " "

linkstr = LINKER +" "+ BIN +" "+ objstr +" "+ LIBS +" "+ LDFLAGS
print('\n',linkstr,'\n')
linkcmd = linkstr.split()
call(linkcmd)