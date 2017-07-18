# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:05:09 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *
from ApConnect import ApConnection
import time

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
        
         #create available
        self.Text_ApAvailable = QLabel("AP not available")   
        self.layout.addWidget(self.Text_ApAvailable, 0, 0)
        
        # create connected
        self.Text_ApConnected = QLabel("AP not connected")
        self.layout.addWidget(self.Text_ApConnected, 1, 0)
        
        # Button to read network card and update avail and connected
        self.Button_CheckStatus = QPushButton("Check AP Status")
        self.layout.addWidget(self.Button_CheckStatus, 0, 1, 2, 1)
        self.Button_CheckStatus.clicked.connect(self.check_ap_status)
        
        #create connection valid
        self.Text_APValidity = QLabel("AP Invalid")
        self.Button_TestValidity = QPushButton("Test Validity")
        self.Button_TestValidity.clicked.connect(self.test_validity)
        
        self.layout.addWidget(self.Text_APValidity, 2, 0)
        self.layout.addWidget(self.Button_TestValidity, 2, 1)
        
        #create host_ip
        self.Line_HostIP = QLineEdit("192.168.1.8") 
        self.Button_SendHostIP = QPushButton("Send host IP")
        self.Button_SendHostIP.clicked.connect(self.send_host_ip)
        
        self.layout.addWidget(self.Line_HostIP, 3, 0)
        self.layout.addWidget(self.Button_SendHostIP, 3, 1)
        
        # create SSID
        self.Line_SSID = QLineEdit("MartianWearablesLLC")
        self.Button_SendSSID = QPushButton("Send SSID")
        self.Button_SendSSID.clicked.connect(self.send_ssid)
        
        self.layout.addWidget(self.Line_SSID, 4, 0)
        self.layout.addWidget(self.Button_SendSSID, 4, 1)
        
        #create password
        self.Line_PASSWORD = QLineEdit("phobicbird712")
        self.Button_SendPASSWORD = QPushButton("Send Password")
        self.Button_SendPASSWORD.clicked.connect(self.send_password)
        
        self.layout.addWidget(self.Line_PASSWORD, 5, 0)
        self.layout.addWidget(self.Button_SendPASSWORD, 5, 1)
        
        # TODO create GO button
        self.Button_FinalizeParams = QPushButton("Finalize Configuration")
        self.layout.addWidget(self.Button_FinalizeParams, 8,0)
        self.Button_FinalizeParams.clicked.connect(self.finalize_params)
        
         # create connect text
        self.Text_ApConnect = QLabel("AP not connected")
        self.layout.addWidget(self.Text_ApConnect, 6, 0)
        
        # Button to connect (only use if available)
        self.Button_Connect = QPushButton("Connect to AP")
        self.layout.addWidget(self.Button_Connect, 6, 1, 2, 1)
        self.Button_Connect.clicked.connect(self.connect_to_ap)
        
        self.Line_PORT = QLineEdit("50007")       
        self.layout.addWidget(self.Line_PORT, 7, 0)
        
    @Slot()
    def finalize_params(self):

        r = self.conn.init_TCP()
        time.sleep(0.5)
        r = self.conn.send_net_params(self.Line_HostIP.text(),
                                      self.Line_SSID.text(),
                                      self.Line_PASSWORD.text(),
                                      self.Line_PORT.text())
        
        msgBox = QMessageBox()
        msgBox.setText(r)
        msgBox.exec_()
        
    @Slot()
    def check_ap_status(self):

        self._Debug.append("Reading network card, please wait...")        
        
        self.conn.read_network_card()
        
        if self.conn.ApIsAvailable:
            self.Text_ApAvailable.setText("Available")
        else:
            self.Text_ApAvailable.setText("NOT Available")
        
        if self.conn.ApConnected:
            self.Text_ApConnected.setText("Connected")
        else:
            self.Text_ApConnected.setText("NOT Connected")
            
        self._Debug.append("Finished reading network card")
            
    
    @Slot()
    def test_validity(self):
        if self.conn.test_ap_connection():
            self.Text_APValidity.setText("Valid")
        else:
            self.Text_APValidity.setText("NOT Valid")
    
    def check_availability(self):
        self.check_ap_status()
        if self.conn.ApConnected and self.conn.ApIsAvailable:
            return True
        else:
            msg = QMessageBox()
            msg.setText("Not connected to AP")
            msg.exec_()
            return False
    
    @Slot()
    def send_host_ip(self):
        if not self.check_availability(): return
        r = self.conn.query_ap('host_ip_'+self.Line_HostIP.text()+'_endhost_ip')
        msgBox = QMessageBox()
        if 'host_ip' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
            
    
    @Slot()
    def send_ssid(self):
        if not self.check_availability(): return
        r = self.conn.query_ap('ssid_'+self.Line_SSID.text()+'_endssid')
        msgBox = QMessageBox()
        if 'SSID' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
    
    @Slot()
    def send_password(self):
        if not self.check_availability(): return
        r = self.conn.query_ap('pass_'+self.Line_PASSWORD.text()+'_endpass')
        msgBox = QMessageBox()
        if 'pass' in r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
        
    @Slot()
    def connect_to_ap(self):
        r = self.conn.connect_to_ap()
        msgBox = QMessageBox()
        if r:
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
        