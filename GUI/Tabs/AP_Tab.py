# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:05:09 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *
from ApConnect import ApConnection

class AP_TAB(QWidget):
    
    def __init__(self, Debug, parent=None):
        super(AP_TAB, self).__init__(parent)
        self._Debug = Debug
        self.conn = ApConnection()
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        #TODO self.layout.setColumnStretch(3,1)
        
         #TODO create available
        self.Text_ApAvailable = QLabel("AP not available")   
        self.layout.addWidget(self.Text_ApAvailable, 0, 0)
        
        # TODO create connected
        self.Text_ApConnected = QLabel("AP not connected")
        self.layout.addWidget(self.Text_ApConnected, 1, 0)
        
        # Button to read network card and update avail and connected
        self.Button_CheckStatus = QPushButton("Check AP Status")
        self.layout.addWidget(self.Button_CheckStatus, 0, 1, 2, 1)
        self.Button_CheckStatus.clicked.connect(self.check_ap_status)
        
        #TODO create connection valid
        self.Text_APValidity = QLabel("AP Invalid")
        self.Button_TestValidity = QPushButton("Test Validity")
        self.Button_TestValidity.clicked.connect(self.test_validity)
        
        self.layout.addWidget(self.Text_APValidity, 2, 0)
        self.layout.addWidget(self.Button_TestValidity, 2, 1)
        
        #TODO TODO create host_ip
        self.Line_HostIP = QLineEdit("192.168.1.8") #TODO get this dynamicaly
        self.Button_SendHostIP = QPushButton("Send host IP")
        self.Button_SendHostIP.clicked.connect(self.send_host_ip)
        
        self.layout.addWidget(self.Line_HostIP, 3, 0)
        self.layout.addWidget(self.Button_SendHostIP, 3, 1)
        
        # TODO create SSID
        self.Line_SSID = QLineEdit("PHSL2")
        self.Button_SendSSID = QPushButton("Send SSID")
        self.Button_SendSSID.clicked.connect(self.send_ssid)
        
        self.layout.addWidget(self.Line_SSID, 4, 0)
        self.layout.addWidget(self.Button_SendSSID, 4, 1)
        
        #TODO create password
        self.Line_PASSWORD = QLineEdit("BSJKMVQ6LF2XH6BJ")
        self.Button_SendPASSWORD = QPushButton("Send Password")
        self.Button_SendPASSWORD.clicked.connect(self.send_password)
        
        self.layout.addWidget(self.Line_PASSWORD, 5, 0)
        self.layout.addWidget(self.Button_SendPASSWORD, 5, 1)
        
        # TODO create GO button
        
        
    @Slot()
    def check_ap_status(self):
        self.conn.read_network_card()
        
        if self.conn.ApIsAvailable:
            self.Text_ApAvailable.setText("Available")
        else:
            self.Text_ApAvailable.setText("NOT Available")
        
        if self.conn.ApConnected:
            self.Text_ApConnected.setText("Connected")
        else:
            self.Text_ApConnected.setText("NOT Connected")
            
    
    @Slot()
    def test_validity(self):
        if self.conn.test_ap_connection():
            self.Text_APValidity.setText("Valid")
        else:
            self.Text_APValidity.setText("NOT Valid")
    
    @Slot()
    def send_host_ip(self):
        r = self.conn.query_ap('host_ip_'+self.Line_HostIP.text()+'_endhost_ip')
        msgBox = QMessageBox()
        if 'host_ip' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
            
    
    @Slot()
    def send_ssid(self):
        r = self.conn.query_ap('ssid_'+self.Line_SSID.text()+'_endssid')
        msgBox = QMessageBox()
        if 'SSID' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
    
    @Slot()
    def send_password(self):
        r = self.conn.query_ap('pass_'+self.Line_PASSWORD.text()+'_endpass')
        msgBox = QMessageBox()
        if 'pass' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
        