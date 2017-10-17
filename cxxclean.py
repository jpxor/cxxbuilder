
""" Cleans C/C++ source """

import os

ROOTDIR = "../src"

#remove all .obj files
for (path, dirnames, filenames) in os.walk(ROOTDIR):
    for filename in filenames:
        if filename.lower().endswith(".o"):
            objpath = os.path.join(path, filename)
            os.remove(objpath)
