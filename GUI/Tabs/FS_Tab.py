# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 19:47:40 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *
from Controller.Modules.Spiffs import SPIFFS

class FS_TAB(QWidget):
    
    SIG_reserve_tcp_buffer = Signal()    
    
    # Define Init Method
    def __init__(self, Device, Debug):
        super(FS_TAB, self).__init__(None)
        self._Debug = Debug
        
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        self._FS = SPIFFS(Device)
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        #TODO self.layout.setColumnStretch(3,1)
        self.layout.setRowStretch(6,1)
        
        #######################################################################
        # Get File system info
        #######################################################################
        self.Text_FsInfo = QTextEdit("file system info goes here...")
        self.Text_FsInfo.setReadOnly(True)
        self.Button_GetFsInfo = QPushButton("Get FS Info")
        
        self.layout.addWidget(self.Text_FsInfo, 0, 0, 2, 1)
        self.layout.addWidget(self.Button_GetFsInfo, 0, 1, 2, 1)
        
        self.Button_GetFsInfo.clicked.connect(self.get_fs_info)
        
        #######################################################################
        # Get network parameters
        #######################################################################
        self.Text_NetParams = QTextEdit("net params go here")
        self.Text_NetParams.setReadOnly(True)
        self.Button_GetNetparams = QPushButton("Get Network params")
        
        self.layout.addWidget(self.Text_NetParams, 4, 0, 1, 1)
        self.layout.addWidget(self.Button_GetNetparams, 4, 1, 1, 1)
        
        self.Button_GetNetparams.clicked.connect(self.get_net_params)
        
        #######################################################################
        # Get command map
        #######################################################################
        self.Text_CommandMap = QTextEdit("Command map goes here")
        self.Text_CommandMap.setReadOnly(True)
        self.Button_GetCommandMap = QPushButton("Get Command Map")
        self.Button_PullFromBuff = QPushButton("Read buffer")
        self.Button_ClearCommandText = QPushButton("Clear command text")
        
        self.layout.addWidget(self.Text_CommandMap, 5, 0, 3, 1)
        self.layout.addWidget(self.Button_GetCommandMap, 5, 1)
        self.layout.addWidget(self.Button_PullFromBuff, 6, 1)
        self.layout.addWidget(self.Button_ClearCommandText, 7, 1)        
        
        self.Button_GetCommandMap.clicked.connect(self.get_command_map)
        self.Button_PullFromBuff.clicked.connect(self.read_tcp_buff)
        self.Button_ClearCommandText.clicked.connect(self.clear_command_map)
        
        #######################################################################
        # Format File System
        #######################################################################
        self.Button_FormatFS = QPushButton("Format File System")
        
        self.layout.addWidget(self.Button_FormatFS, 8, 0, 1, 1)
        
        self.Button_FormatFS.clicked.connect(self.fs_format)
        
    @Slot()
    def read_tcp_buff(self):
        current = self.Text_CommandMap.toPlainText()
        r = self._FS.readTcpBuff()
        self.Text_CommandMap.setText(current+r)
        
    @Slot()
    def clear_command_map(self):
        self.Text_CommandMap.setText("")
        
    @Slot()
    def get_fs_info(self):
        r = self._FS.getFsInfo()
        self.Text_FsInfo.setText(r)
    
    @Slot()
    def get_net_params(self):
        r = self._FS.getNetworkParams()
        self.Text_NetParams.setText(r)
        
    @Slot()
    def get_command_map(self):
        #Disable auto_connect
        self.SIG_reserve_tcp_buffer.emit()
        self.Text_CommandMap.setText("retrieving command map...")
        r = self._FS.getCommandMap()
        self.Text_CommandMap.setText(r)
    
    @Slot()
    def fs_format(self):
        r = self._FS.formatFs() #TODO add confirmation waiting here
        msgBox = QMessageBox()
        msgBox.setText(r)
        msgBox.exec_()
        





















