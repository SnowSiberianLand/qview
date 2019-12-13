# -*- coding: cp1251 -*-
import os
import mod_dproc
mod_dproc.init_lib_dproc()
from UI import MainPWindows
from PySide.QtGui import *


global app
app = None

app = QApplication([])
mnp = MainPWindows()
mnp.show()
app.exec_()