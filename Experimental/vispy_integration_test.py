# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 06:47:12 2017

@author: marzipan
"""
#==============================================================================
# 
# from PySide.QtCore import *
# from PySide.QtGui import *
#==============================================================================
from vispy.plot import Fig
import sys

#app = QApplication(sys.argv)
#win = QMainWindow()

#plt.plot([1,2,3,4], [1,4,9,16])
fig= Fig()

#vispyCanvas=plt.show()[0]
#win.setCentralWidget(vispyCanvas.native)


ax = fig[0, 0]

import numpy as np
data = np.random.randn(3, 1)
ax.plot(data)

#TODO get this to use pyside...








