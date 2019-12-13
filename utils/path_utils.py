import os
import sys

import mod_cmn as cmn

def binPath():
    path = cmn.getAppOptions().getApplicationPath()
    return os.path.abspath(str(path))

def pythonPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/')
    return os.path.abspath(str(path))

def pythonLibsPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/python_libs/')
    return os.path.abspath(str(path))

def numpyPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/numpy/')
    return os.path.abspath(str(path))

def scipyPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/scipy/')
    return os.path.abspath(str(path))

def matplotlibPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/matplotlib/')
    return os.path.abspath(str(path))

def dateutilPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/dateutil/')
    return os.path.abspath(str(path))

def mplToolkitsPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/mpl_toolkits/')
    return os.path.abspath(str(path))

def tkinterPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/tkinter/')
    return os.path.abspath(str(path))

def tornadoPath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/tornado/')
    return os.path.abspath(str(path))

def scriptPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../')
    return os.path.abspath(str(path))

def utilsPath():
    return os.path.abspath(__file__)

def internalPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../internal/')
    return os.path.abspath(str(path))

def sitePath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python34.zip/site-packages')
    return os.path.abspath(str(path))

def pysidePath():
    bin_path = binPath()
    path = os.path.join(bin_path, '/python/PySide/')
    return os.path.abspath(str(path))

if binPath() in sys.path:
    sys.path.remove(binPath())
sys.path.insert(0, binPath())

if pythonPath() in sys.path:
    sys.path.remove(pythonPath())
sys.path.insert(0, pythonPath())

if pythonLibsPath() in sys.path:
    sys.path.remove(pythonLibsPath())
sys.path.insert(0, pythonLibsPath())

if numpyPath() in sys.path:
    sys.path.remove(numpyPath())
sys.path.insert(0, numpyPath())

if scipyPath() in sys.path:
    sys.path.remove(scipyPath())
sys.path.insert(0, scipyPath())

if matplotlibPath() in sys.path:
    sys.path.remove(matplotlibPath())
sys.path.insert(0, matplotlibPath())

if dateutilPath() in sys.path:
    sys.path.remove(dateutilPath())
sys.path.insert(0, dateutilPath())

if mplToolkitsPath() in sys.path:
    sys.path.remove(mplToolkitsPath())
sys.path.insert(0, mplToolkitsPath())

if tkinterPath() in sys.path:
    sys.path.remove(tkinterPath())
sys.path.insert(0, tkinterPath())

if tornadoPath() in sys.path:
    sys.path.remove(tornadoPath())
sys.path.insert(0, tornadoPath())

if scriptPath() in sys.path:
    sys.path.remove(scriptPath())
sys.path.insert(0, scriptPath())

if utilsPath() in sys.path:
    sys.path.remove(utilsPath())
sys.path.insert(0, utilsPath())

if internalPath() in sys.path:
    sys.path.remove(internalPath())
sys.path.insert(0, internalPath())

if sitePath() in sys.path:
    sys.path.remove(sitePath())
sys.path.insert(0, sitePath())

if pysidePath() in sys.path:
    sys.path.remove(pysidePath())
sys.path.insert(0, pysidePath())