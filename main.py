# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 14:42:24 2017

@author: MartianMartin
"""

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import sys
import time

import qdarkstyle

from GUI.GUI_Home import AlphaScanGui
from Controller.DeviceCluster import DeviceCluster

try:
    qt_app = QtGui.QApplication(sys.argv)
except RuntimeError as e: # could fail for reasons other than already exists... 
    qt_app = QtGui.QApplication.instance()
    print("Qt Application already exists, reusing...")

#qt_app.setStyle(u'Cleanlooks')
qt_app.setStyleSheet(qdarkstyle.load_stylesheet())

if len(sys.argv) >= 2:
    fileName = sys.argv[1]
else:
    fileName = "."
    
# Run app     
dev = DeviceCluster(num_devices=2,starting_port=50007)
app = AlphaScanGui(dev, fileName)
time.sleep(0.01)
app.show()
qt_app.exec_()
























