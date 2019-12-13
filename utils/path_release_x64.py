
import os
import sys

def binPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../../../../../build/win64/bin/release')
    return os.path.abspath(path)

def utilsPath():
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '../../../../../data/juno_init/settings/scripts/utils')
    return os.path.abspath(path)



if not binPath() in sys.path:
    sys.path.append(binPath())
if not utilsPath() in sys.path:
    sys.path.append(utilsPath())