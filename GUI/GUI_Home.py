# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 16:42:21 2016

@author: marzipan
"""

###############################################################################
# AlphaScan GUI Home Page #####################################################
###############################################################################

from PySide.QtCore import *
from PySide.QtGui import *
#import qdarkstyle 
import sys
import time

from GEN_Tab import GeneralTab
from ACCEL_Tab import ACCEL_REG_TAB
from ADC_Tab import ADC_REG_TAB
from PWR_Tab import PWR_REG_TAB
from AP_Tab import AP_TAB
from FS_Tab import FS_TAB
from SYS_Tab import SYS_TAB

from AlphaScanController import AlphaScanDevice

try:
    qt_app = QApplication(sys.argv)
except: # could fail for reasons other than already exists... 
    pass

#qt_app.setStyleSheet(qdarkstyle.load_stylesheet())

class AlphaScanGui(QWidget): #TODO probably want something other than dialog here
    def __init__(self, Device, fileName, parent=None):
        super(AlphaScanGui, self).__init__(parent)
        self._Device = Device
        
        # Creat main layout
        mainLayout =  QVBoxLayout()
        self.setLayout(mainLayout)
        
        # Create tab widget
        tabWidget =  QTabWidget()
        mainLayout.addWidget(tabWidget)
        
        # Create persistent status area
        statusArea = QVBoxLayout()
        mainLayout.addLayout(statusArea)
        
        # Add device streaming and connected labels to status area
        self.StreamingStatus = QLabel("Not Streaming") #TODO connect these
        self.ConnectionStatus = QLabel("Not Connected")
        
        statusArea.addWidget(self.StreamingStatus)
        statusArea.addWidget(self.ConnectionStatus)

        # Create tab objects        
        self.genTab = GeneralTab(self._Device)        
        
        # Create tabs with objects
        tabWidget.addTab(self.genTab, "General")
        tabWidget.addTab(ADC_REG_TAB(self._Device), "ADC")
        tabWidget.addTab(PWR_REG_TAB(self._Device), "Power")
        tabWidget.addTab(ACCEL_REG_TAB(self._Device), "Accel")
        tabWidget.addTab(AP_TAB(),"AcessPoint")
        tabWidget.addTab(FS_TAB(self._Device), "FileSystem")
        tabWidget.addTab(SYS_TAB(self._Device), "McuParams")

        self.setWindowTitle("AlphaScan Controller")
        
        # Create periodic timer for updating streaming and connection status
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        
    @Slot()
    def update(self):
        if self.genTab.Streaming:
            self.StreamingStatus.setText("Streaming")
        else:
            self.StreamingStatus.setText("Not Streaming")
        if self.genTab.Connected:
            self.ConnectionStatus.setText("Connected")
        else:
            self.ConnectionStatus.setText("Not Connected")
        
    def closeEvent(self, event):
        self._Device.close_TCP()
        self._Device.close_UDP()
        event.accept()
        
    def run(self):
        # Show the form
        self.show()
        # Run the qt application
        qt_app.exec_()

###############################################################################
# RUN APPLICATION #############################################################
###############################################################################

if len(sys.argv) >= 2:
    fileName = sys.argv[1]
else:
    fileName = "."
    
# Run app     
dev = AlphaScanDevice() 
app = AlphaScanGui(dev, fileName)
time.sleep(0.01)
app.run()
            
            
       
       
       
       
       
       
