

import os
import sys


def binPath():
    path = 'c:/jenkins/work_bins/rv7_0_binaries/rv-win64/'
    return os.path.abspath(str(path))
    
def pythonPath():
    path = 'c:/jenkins/work_bins/rv7_0_binaries/rv-win64/python/'
    return os.path.abspath(str(path))

def utilsPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../utils/')
    return os.path.abspath(str(path))

def sitePath():
    path = 'c:/jenkins/work_bins/rv7_0_binaries/rv-win64/python34.zip/site-packages/'
    return os.path.abspath(str(path))
    
def libsPath():
    path = 'c:/jenkins/work_bins/rv7_0_binaries/rv-win64/python/python_libs/'
    return os.path.abspath(str(path))
    
def opsPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../ops/')
    return os.path.abspath(str(path))

if not binPath() in sys.path:
    sys.path.append(binPath())
    
if not pythonPath() in sys.path:
    sys.path.append(pythonPath())

if not utilsPath() in sys.path:
    sys.path.append(utilsPath())
    
if not sitePath() in sys.path:
    sys.path.append(sitePath())

if not opsPath() in sys.path:
    sys.path.append(opsPath())

if not libsPath() in sys.path:
    sys.path.append(libsPath())