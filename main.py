# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 14:42:24 2017

@author: MartianMartin
"""

from PySide.QtCore import *
from PySide.QtGui import * 
import sys
import time

from GUI.GUI_Home import AlphaScanGui
from Controller.DeviceCluster import DeviceCluster

try:
    qt_app = QApplication(sys.argv)
except: # could fail for reasons other than already exists... 
    pass

qApp.setStyle(u'Cleanlooks')
#qt_app.setStyleSheet(qdarkstyle.load_stylesheet())

if len(sys.argv) >= 2:
    fileName = sys.argv[1]
else:
    fileName = "."
    
# Run app     
dev = DeviceCluster(num_devices=2) 
app = AlphaScanGui(dev, fileName)
time.sleep(0.01)
app.show()
qt_app.exec_()
