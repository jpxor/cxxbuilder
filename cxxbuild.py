
""" Builds C/C++ source based on config file inputs """

import os
import sys
from subprocess import call

if len(sys.argv) != 3:
    print("Requires build config files as input")
    print()
    print("Example usage:")
    print("python cxxbuilder.py project.config platform.config")
    exit()

project_file = sys.argv[1]
platform_file = sys.argv[2]

def indexof(list, item):
    i = 0
    for listitem in list:
        listitem = listitem.strip()
        if listitem == item:
            return i
        i += 1
    print("failed to parse config, can't find item:", item)
    exit(-1)

def getList(items, idx):
    list = []
    while idx < len(items):
        target = items[idx].strip()
        if target != "":
            list.append(target)
            idx += 1
        else: break
    return list

#load project configs
with open(project_file) as projectfile:
    projectconfig = projectfile.readlines()

idx = indexof(projectconfig, "ROOT_DIR:")
ROOT_DIR = projectconfig[idx+1].strip()

idx = indexof(projectconfig, "BIN:")
BIN = projectconfig[idx+1].strip()

idx = indexof(projectconfig, "BIN_DIR:")
BIN_DIR = projectconfig[idx+1].strip()

idx = indexof(projectconfig, "TARGETS:")
TARGETS = getList(projectconfig, idx+1)

idx = indexof(projectconfig, "INCLUDE_DIRS:")
INCLUDE_DIRS = getList(projectconfig, idx+1)

LIBS = {}
for target in TARGETS:
    idx = indexof(projectconfig, "LIBS:"+target)
    LIBS[target] = getList(projectconfig, idx+1)

#load platform configs
with open(platform_file) as platformfile:
    platformconfig = platformfile.readlines()

idx = indexof(platformconfig, "TARGET:")
TARGET = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "INC_PREFIX:")
INC_PREFIX = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "LIB_PREFIX:")
LIB_PREFIX = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "BIN_SUFFIX:")
BIN_SUFFIX = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "CXXFLAGS:")
CXXFLAGS = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "LDFLAGS:")
LDFLAGS = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "LIBS:")
PLATFORM_LIBS = getList(platformconfig, idx+1)
LIBS[TARGET] += PLATFORM_LIBS

idx = indexof(platformconfig, "COMPILER:")
COMPILER_STR = platformconfig[idx+1].strip()

idx = indexof(platformconfig, "LINKER:")
LINKER_STR = platformconfig[idx+1].strip()

BIN_TARGET = BIN_DIR + "/" + TARGET
BIN_PATH = BIN_TARGET + "/" + BIN + BIN_SUFFIX

if not os.path.exists(BIN_TARGET):
    os.makedirs(BIN_TARGET)

print()
print("::BUILD CONFIGURATION:: ")
print()
print("Target:\n ",TARGET)
print()
print("Binary:\n ", BIN_PATH)
print()
print("Commands: ")
print(" ",COMPILER_STR)
print(" ",LINKER_STR)
print()
print("CXXFLAGS:\n ",CXXFLAGS)
print()
print("LDFLAGS:\n ",LDFLAGS)
print()
print("Includes:\n ",INCLUDE_DIRS)
print()
print("Libs:\n ",LIBS[TARGET])
print()

INCLUDE_STR = ""
for inc in INCLUDE_DIRS:
    INCLUDE_STR += (INC_PREFIX + inc + " ")

LIBS_STR = ""
for lib in LIBS[TARGET]:
    LIBS_STR += (LIB_PREFIX + lib + " ")

COMPILER_STR = COMPILER_STR.replace("{INCLUDE_DIRS}", INCLUDE_STR)
COMPILER_STR = COMPILER_STR.replace("{CXXFLAGS}", CXXFLAGS)

LINKER_STR = LINKER_STR.replace("{BIN_DIR}/{TARGET}/{BIN}{BIN_SUFFIX}", BIN_PATH)
LINKER_STR = LINKER_STR.replace("{LDFLAGS}", LDFLAGS)

def find_path(filename):
    """ find and return the pathname to filename """
    for (path, dirnames, filenames) in os.walk(ROOT_DIR):
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
    ccstr = COMPILER_STR
    ccstr = ccstr.replace("{OBJ_PATH}", objpath)
    ccstr = ccstr.replace("{SRC_PATH}", srcpath)
    print('\n', ccstr, '\n')
    cccmd = ccstr.split(' ')
    cccmd = list(filter(None, cccmd)) 
    call(cccmd)

objfilelist = []
#compile each c/cpp file under PWD
for (path, dirnames, filenames) in os.walk(ROOT_DIR):
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
OBJ_STR = "" 
for obj in objfilelist:
    OBJ_STR += obj + " "

LIBS_STR = "" 
for lib in LIBS[TARGET]:
    LIBS_STR += LIB_PREFIX + lib + " "

LINKER_STR = LINKER_STR.replace("{OBJ_FILES}", OBJ_STR)
LINKER_STR = LINKER_STR.replace("{LIBS}", LIBS_STR) 
print('\n', LINKER_STR, '\n')
linkcmd = LINKER_STR.split()
call(linkcmd)