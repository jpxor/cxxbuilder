"""
MIT License

Copyright (c) 2017 Josh Simonot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#!/usr/bin/python

import os
import sys
from subprocess import call

"""
cxxbuild.py

Recursively searches through source directories rebuilding
any C/C++ source files that have been changed since the last
build. This script also scans the source files' included header
files to determine whether they have changed as well.

How the source is built is configured via a project config file and
a platform/build system specific config file passed in as arguments.
"""

"""
Check for valid input arguments
"""

if len(sys.argv) != 3:
    print("Requires build config files as input")
    print()
    print("Example usage:")
    print("python cxxbuild.py project.config platform.config")
    exit(-1)

PROJECT_FILE = sys.argv[1]
PLATFORM_FILE = sys.argv[2]

if not os.path.isfile(PROJECT_FILE):
    print("ERROR not a file:", PROJECT_FILE)
    print()
    print("Example usage:")
    print("python cxxbuild.py project.config platform.config")
    exit(-2)

if not os.path.isfile(PLATFORM_FILE):
    print("ERROR not a file:", PLATFORM_FILE)
    print()
    print("Example usage:")
    print("python cxxbuild.py project.config platform.config")
    exit(-3)

#project config
with open(PROJECT_FILE) as file:
    PROJECT_CONFIG = file.readlines()

#load platform configs
with open(PLATFORM_FILE) as file:
    PLATFORM_CONFIG = file.readlines()

"""
Util functions for reading the config files
"""

def indexof(ilist, item):
    """ returns the index of item in the list """
    i = 0
    for list_item in ilist:
        list_item = list_item.strip()
        if list_item == item:
            return i
        i += 1
    print("ERROR failed to parse config, can't find item:", item)
    exit(-4)


def sublist(full_list, index):
    """ returns a sub-list of contiguous non-emtpy lines starting at index """
    sub_list = []
    while index < len(full_list):
        line = full_list[index].strip()
        if line != "":
            sub_list.append(line)
            index += 1
        else: break
    return sub_list


"""
Read config files into global vars
"""

idx = indexof(PROJECT_CONFIG, "ROOT_DIR:")
ROOT_DIR = PROJECT_CONFIG[idx+1].strip()

idx = indexof(PROJECT_CONFIG, "BIN:")
BIN = PROJECT_CONFIG[idx+1].strip()

idx = indexof(PROJECT_CONFIG, "BIN_DIR:")
BIN_DIR = PROJECT_CONFIG[idx+1].strip()

idx = indexof(PROJECT_CONFIG, "TARGETS:")
TARGETS = sublist(PROJECT_CONFIG, idx+1)

idx = indexof(PROJECT_CONFIG, "INCLUDE_DIRS:")
INCLUDE_DIRS = sublist(PROJECT_CONFIG, idx+1)

LIBS = {}
for target in TARGETS:
    idx = indexof(PROJECT_CONFIG, "LIBS:"+target)
    LIBS[target] = sublist(PROJECT_CONFIG, idx+1)

idx = indexof(PLATFORM_CONFIG, "TARGET:")
TARGET = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "INC_PREFIX:")
INC_PREFIX = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "LIB_PREFIX:")
LIB_PREFIX = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "BIN_SUFFIX:")
BIN_SUFFIX = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "CXXFLAGS:")
CXXFLAGS = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "LDFLAGS:")
LDFLAGS = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "LIBS:")
PLATFORM_LIBS = sublist(PLATFORM_CONFIG, idx+1)
LIBS[TARGET] += PLATFORM_LIBS

idx = indexof(PLATFORM_CONFIG, "COMPILER:")
COMPILER_STR = PLATFORM_CONFIG[idx+1].strip()

idx = indexof(PLATFORM_CONFIG, "LINKER:")
LINKER_STR = PLATFORM_CONFIG[idx+1].strip()

BIN_TARGET = BIN_DIR + "/" + TARGET
BIN_PATH = BIN_TARGET + "/" + BIN + BIN_SUFFIX

"""
Print configuration information
"""

print()
print("::BUILD CONFIGURATION:: ")
print()
print("Target:\n ", TARGET)
print()
print("Binary:\n ", BIN_PATH)
print()
print("Commands: ")
print(" ", COMPILER_STR)
print(" ", LINKER_STR)
print()
print("CXXFLAGS:\n ", CXXFLAGS)
print()
print("LDFLAGS:\n ", LDFLAGS)
print()
print("Includes:\n ", INCLUDE_DIRS)
print()
print("Libs:\n ", LIBS[TARGET])
print()

"""
Prepare values for compiling
"""

INCLUDE_STR = ""
for inc in INCLUDE_DIRS:
    INCLUDE_STR += (INC_PREFIX + inc + " ")

COMPILER_STR = COMPILER_STR.replace("{INCLUDE_DIRS}", INCLUDE_STR)
COMPILER_STR = COMPILER_STR.replace("{CXXFLAGS}", CXXFLAGS)

"""
Util functions for finding included header files
"""

def find_path(file_name):
    """ find and return the pathname to filename """
    for (cpath, _, fnames) in os.walk(ROOT_DIR):
        if file_name in fnames:
            return os.path.join(cpath, file_name)
    return file_name


def get_headers(src_path):
    """ list all included headers in src """
    headerlist = []
    with open(src_path, 'r') as srcfile:
        lines = srcfile.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#include"):
                headername = line[10:-1].strip()
                headerpath = find_path(headername)
                headerlist.append(headerpath)
    return headerlist

"""
Util functions for compiling
"""

def needs_recompile(src_path, obj_path):
    """ determine if src file needs recompile """

    #check if obj file exists
    if not os.path.isfile(obj_path):
        print("\nBuilding:", src_path)
        return True

    #check src file modification time
    if os.path.getmtime(src_path) > os.path.getmtime(obj_path):
        print("\nRebuilding:", src_path)
        return True

    #check header files' modification time
    for header_path in get_headers(src_path):
        header_path = header_path.rstrip()
        if os.path.isfile(header_path):
            if os.path.getmtime(header_path) > os.path.getmtime(obj_path):
                print("\nRebuilding:", src_path)
                return True

    print("Nothing to be done for:", src_path)
    return False


def compile_src(src_path, obj_path):
    """ compile the source file """
    ccstr = COMPILER_STR

    ccstr = ccstr.replace("{OBJ_PATH}", obj_path)
    ccstr = ccstr.replace("{SRC_PATH}", src_path)

    #provide compile cmd to users
    print('\n', ccstr, '\n')

    cccmd = list(filter(None, ccstr.split(' ')))
    call(cccmd)

"""
Util functions for linking
"""

def link_objs(obj_list):
    """ link the object files """
    ldstr = LINKER_STR

    obj_str = ""
    for obj in obj_list:
        obj_str += (obj + " ")

    libs_str = ""
    for lib in LIBS[TARGET]:
        libs_str += (LIB_PREFIX + lib + " ")

    ldstr = ldstr.replace("{BIN_DIR}/{TARGET}/{BIN}{BIN_SUFFIX}", BIN_PATH)
    ldstr = ldstr.replace("{LDFLAGS}", LDFLAGS)
    ldstr = ldstr.replace("{OBJ_FILES}", obj_str)
    ldstr = ldstr.replace("{LIBS}", libs_str)

    #provide link cmd to users
    print('\n', LINKER_STR, '\n')

    linkcmd = list(filter(None, ldstr.split()))
    call(linkcmd)


"""
Create target bin directory if needed
"""

if not os.path.exists(BIN_TARGET):
    os.makedirs(BIN_TARGET)

"""
Recursively search through the ROOT_DIR, compiling each source file
and storing the path to each object file produced, then link the objects.
"""

OBJECTS = []
for (path, dirnames, filenames) in os.walk(ROOT_DIR):
    for filename in filenames:
        if filename.lower().endswith(".c") or filename.lower().endswith(".cpp"):
            name, ext = os.path.splitext(filename)

            srcpath = os.path.join(path, filename)
            objpath = os.path.join(path, name) + ".o"

            OBJECTS.append(objpath)

            if needs_recompile(srcpath, objpath):
                compile_src(srcpath, objpath)

link_objs(OBJECTS)
