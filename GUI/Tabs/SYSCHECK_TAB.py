# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 16:38:14 2017

@author: marzipan
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 20:53:39 2017

@author: MartianMartin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:05:09 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

class SYSCHECK_TAB(QWidget):
    
    def __init__(self, Debug, parent=None):
        super(SYSCHECK_TAB, self).__init__(parent)
        self._Debug = Debug
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        
         #create available
        self.Text_ApAvailable = QLabel("Test Label 1")   
        self.layout.addWidget(self.Text_ApAvailable, 0, 0)
        
        # create connected
        self.Text_ApConnected = QLabel("Test Label 2d")
        self.layout.addWidget(self.Text_ApConnected, 1, 0)
        
        # Button to read network card and update avail and connected
        self.Button_CheckStatus = QPushButton("Test Button")
        self.layout.addWidget(self.Button_CheckStatus, 0, 1, 2, 1)
        self.Button_CheckStatus.clicked.connect(self.test_method)
        
        
        
    @Slot()
    def test_method(self):
        
        msgBox = QMessageBox()
        msgBox.setText("Test Message Dialog")
        msgBox.exec_()

    
 

        