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

"""
Cleans C/C++ source by recursively searching the source directories
for object files to delete
"""

"""
Check for valid input arguments
"""

if len(sys.argv) != 2:
    print("Requires project config file as input")
    print()
    print("Example usage:")
    print("python cxxclean.py project.config")
    exit(-1)

PROJECT_FILE = sys.argv[1]

if not os.path.isfile(PROJECT_FILE):
    print("ERROR not a file:", PROJECT_FILE)
    print()
    print("Example usage:")
    print("python cxxclean.py project.config")
    exit(-2)

#project config
with open(PROJECT_FILE) as file:
    PROJECT_CONFIG = file.readlines()

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

"""
Read config files into global vars
"""

IDX = indexof(PROJECT_CONFIG, "ROOT_DIR:")
ROOT_DIR = PROJECT_CONFIG[IDX+1].strip()

#remove all *.o files
for (path, dirnames, filenames) in os.walk(ROOT_DIR):
    for filename in filenames:
        if filename.lower().endswith(".o"):
            objpath = os.path.join(path, filename)
            os.remove(objpath)
