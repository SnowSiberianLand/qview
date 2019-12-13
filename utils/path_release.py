
import os
import sys

def binPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../../../')
    return os.path.abspath(path)

def utilsPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../utils')
    return os.path.abspath(path)



if not binPath() in sys.path:
    sys.path.append(binPath())
if not utilsPath() in sys.path:
    sys.path.append(utilsPath())