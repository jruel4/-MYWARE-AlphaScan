# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 01:17:03 2017

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *
import gc

''' Test vispy code '''
from vispy_plotter import Canvas

class VIZ_TAB(QWidget):
    
    SIG_reserve_tcp_buffer = Signal()
    
    # Define Init Method
    def __init__(self, Device, Debug):
        super(VIZ_TAB, self).__init__(None)
        
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        self._Device = Device
        self._Debug = Debug
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        
        #######################################################################
        # Display system parameters
        #######################################################################
        
        
        
    @Slot()
    def test_message(self):
        r = "test message"
        msg = QMessageBox()
        msg.setText(r)
        msg.exec_()
        
    @Slot()
    def start_plotting(self):
        # Create and Add widget   
        self.fig = Canvas()
        self.layout.addWidget(self.fig.native, 0, 0) 
        self._Debug.append("start plotting")

    @Slot()
    def stop_plotting(self):
        # Override on timer method of fig
        functype = type(self.fig.on_timer)
        def do_nothing(a,b):pass
        self.fig.on_timer = functype(do_nothing, self.fig, Canvas)        

        






















