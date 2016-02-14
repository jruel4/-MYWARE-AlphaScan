# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:06:33 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

class GeneralTab(QWidget):
    
    # Define Init Method
    def __init__(self,Device):
        super(GeneralTab, self).__init__(None)
        
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        self._Device = Device        
        
        # Define status vars
        self.Connected = False
        self.Streaming = False
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setColumnStretch(3,1)
        # TODO prevent horizontal stretch
        
        #######################################################################
        # Status Row ##########################################################
        #######################################################################
        
        # Create Status items to Row_ConnectStatus
        self.Text_ConnectStatus = QLabel("Device is Disconnected")
        self.Button_Connect = QPushButton("CONNECT")
        self.Button_Disconnect = QPushButton("DISCONNECT")
        
        # Add status items to status row
        self.layout.addWidget(self.Text_ConnectStatus,0,0)
        self.layout.addWidget(self.Button_Connect,0,1)
        self.layout.addWidget(self.Button_Disconnect,0,2)
        
        # Connect Status button signals to connection control slots
        self.Button_Connect.clicked.connect(self.connect_to_device)
        self.Button_Disconnect.clicked.connect(self.disconnect_from_device)   
        
        #######################################################################
        # Accelerometer Row ###################################################
        #######################################################################
        
        # Create Accel Status items
        self.Text_AccelStatus = QLabel("Please update accel status")
        self.Button_RefreshAccelStatus = QPushButton("Update Accel Status")
        
        # Add status items to Row_AccelStatus
        self.layout.addWidget(self.Text_AccelStatus,1,0)
        self.layout.addWidget(self.Button_RefreshAccelStatus,1,1,1,2)
        
        # Connect Accel Status button signals to slots
        self.Button_RefreshAccelStatus.clicked.connect(self.update_accel_status)
        
        #######################################################################
        # Power Management Row ################################################
        #######################################################################
        
        # Create PwrManage items
        self.Text_PowerStatus = QLabel("Please update power status")
        self.Button_RefreshPowerStatus = QPushButton("Update Power Status")
        
        # Add status items to Row_PowerManage
        self.layout.addWidget(self.Text_PowerStatus,2,0)
        self.layout.addWidget(self.Button_RefreshPowerStatus,2,1,1,2)
        
        # Connect Power Manage button signals to slots
        self.Button_RefreshPowerStatus.clicked.connect(self.update_power_status)
        
        #######################################################################
        # ADC Row #############################################################
        #######################################################################
        
        # Create adc mamangement items
        self.Text_AdcStatus = QLabel("Please update ADC Status")
        self.Button_RefreshAdcStatus = QPushButton("Update ADC Status")
        
        self.Text_AdcStreamStatus = QLabel("ADC not streaming")
        self.Button_AdcBeginStream = QPushButton("Begin Stream")
        self.Button_AdcStopStream = QPushButton("Stop Stream")
        
        # Add status/control widgets to Adc layout
        self.layout.addWidget(self.Text_AdcStatus, 3,0)
        self.layout.addWidget(self.Button_RefreshAdcStatus, 3,1,1,2)
        
        self.layout.addWidget(self.Text_AdcStreamStatus, 4,0,)
        self.layout.addWidget(self.Button_AdcBeginStream, 4,1)
        self.layout.addWidget(self.Button_AdcStopStream, 4,2)
        
        # Connect ADC signal to slots
        self.Button_RefreshAdcStatus.clicked.connect(self.update_adc_status)
        
        self.Button_AdcBeginStream.clicked.connect(self.begin_streaming)
        self.Button_AdcStopStream.clicked.connect(self.stop_streaming)
        
        #######################################################################
        # General Message Area ################################################
        #######################################################################
        
        # Create general message label
        self.Text_GeneralMessage = QLabel("")
        self.layout.addWidget(self.Text_GeneralMessage, 5,0,1,2)
        
        # Add message formatting
        self.Text_GeneralMessage.setAutoFillBackground(True)
        p = self.Text_GeneralMessage.palette()
        p.setColor(self.Text_GeneralMessage.backgroundRole(), 'cyan')
        self.Text_GeneralMessage.setPalette(p)
        
        # Add clear general message button
        self.Button_ClearGeneralMessage = QPushButton("Clear Message")
        self.layout.addWidget(self.Button_ClearGeneralMessage, 5,2,1,1)
        self.Button_ClearGeneralMessage.clicked.connect(self.clear_gen_msg)
        

        
        #######################################################################
        # UDP Stream Statistics ###############################################
        #######################################################################
        
        self.Text_PacketRate = QLabel("Packets / second: ")
        self.Text_Availability = QLabel("Availability: ")
        self.Text_TotalReceived = QLabel("Total Received: ")
        self.Text_TotalDropped = QLabel("Total Dropped: ")
        
        self.Text_PacketRateVAL = QLabel("")
        self.Text_AvailabilityVAL = QLabel("")
        self.Text_TotalReceivedVAL = QLabel("")
        self.Text_TotalDroppedVAL = QLabel("")
        
        self.layout.addWidget(self.Text_PacketRate, 6, 0)
        self.layout.addWidget(self.Text_Availability, 7, 0)
        self.layout.addWidget(self.Text_TotalReceived, 8, 0)
        self.layout.addWidget(self.Text_TotalDropped, 9, 0)
        
        self.layout.addWidget(self.Text_PacketRateVAL, 6, 1)
        self.layout.addWidget(self.Text_AvailabilityVAL, 7, 1)
        self.layout.addWidget(self.Text_TotalReceivedVAL, 8, 1)
        self.layout.addWidget(self.Text_TotalDroppedVAL, 9, 1)
        
        #######################################################################
        # OTA Mode ############################################################
        #######################################################################
        
        self.Button_OtaMode = QPushButton("Enter OTA Mode")
        self.layout.addWidget(self.Button_OtaMode, 10, 0, 1, 1)
        self.Button_OtaMode.clicked.connect(self.enter_ota_mode)
        
        #######################################################################
        # AP Mode #############################################################
        #######################################################################
        
        self.Button_ApMode = QPushButton("Enter AP Mode")
        self.layout.addWidget(self.Button_ApMode, 11, 0, 1, 1)
        self.Button_ApMode.clicked.connect(self.enter_ap_mode)
        
        #######################################################################
        # Update Command Map ##################################################
        #######################################################################
        
        self.Button_UpdateCmdMap = QPushButton("Update Command Map")
        self.layout.addWidget(self.Button_UpdateCmdMap, 12, 0, 1, 1)
        self.Button_UpdateCmdMap.clicked.connect(self.update_command_map)
        
    ###########################################################################
    # Slots ###################################################################
    ###########################################################################
        
    @Slot()
    def connect_to_device(self):
        if self.Connected: return
        self.Text_ConnectStatus.setText("Connecting to AlphaScan...")
        if self._Device.connect_to_device():
            self.Connected = True
            self.Text_ConnectStatus.setText("Connected")
        else:
            self.Text_ConnectStatus.setText("Connection FAILED")
    
    @Slot()
    def disconnect_from_device(self):
        if not self.Connected: return
        self.Text_ConnectStatus.setText("Disconnecting from AlphaScan...")
        self._Device.close_TCP()
        self.Connected = False
        self.Text_ConnectStatus.setText("Disconnected")
        
    @Slot()
    def update_accel_status(self):
        if self.Streaming or not self.Connected:
            self.Text_AccelStatus.setText("ILLEGAL")
            return
        accel_status_string = self._Device.generic_tcp_command_BYTE("ACC_get_status")
        self.Text_AccelStatus.setText(accel_status_string)
        
    @Slot()
    def update_power_status(self):
        if self.Streaming or not self.Connected:
            self.Text_PowerStatus.setText("ILLEGAL")
            return
        power_status_string = self._Device.generic_tcp_command_BYTE("PWR_get_status")
        self.Text_PowerStatus.setText(power_status_string)
        
    @Slot()
    def update_adc_status(self):
        if self.Streaming or not self.Connected:
            self.Text_AdcStatus.setText("ILLEGAL")
            return
        adc_status_string = self._Device.generic_tcp_command_BYTE("ADC_get_register")
        self.Text_AdcStatus.setText(adc_status_string)
    
    @Slot()
    def begin_streaming(self):
        if self.Streaming or not self.Connected:
            self.Text_GeneralMessage.setText("ILLEGAL: Streaming must be false, Connected must be true")
            return
        begin_stream_string = self._Device.initiate_UDP_stream()
        self.Streaming = True # TODO validate
        self.Text_AdcStreamStatus.setText(begin_stream_string)
    
    @Slot()
    def stop_streaming(self):
        if not self.Streaming or not self.Connected:
            self.Text_GeneralMessage.setText("ILLEGAL: Streaming must be true, Connected must be true")
            return
        stat, time, avail, rx, drop = self._Device.terminate_UDP_stream()
        self.Streaming = False # TODO validate
        self.Text_AdcStreamStatus.setText(stat)
        self.Text_AvailabilityVAL.setText(avail)
        self.Text_PacketRateVAL.setText(time)
        self.Text_TotalDroppedVAL.setText(drop)
        self.Text_TotalReceivedVAL.setText(rx)
        
    @Slot()
    def clear_gen_msg(self):
        self.Text_GeneralMessage.setText("")
        
    @Slot()
    def enter_ota_mode(self):
        r = self._Device.generic_tcp_command_BYTE('GEN_start_ota') 
        msgBox = QMessageBox()
        if '' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
        self.disconnect_from_device()
        
    @Slot()
    def enter_ap_mode(self):
        r = self._Device.generic_tcp_command_BYTE('GEN_start_ap') 
        msgBox = QMessageBox()
        if '' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText("failure")
        msgBox.exec_()
    
    @Slot()
    def update_command_map(self):
        r = self._Device.update_command_map()
        msgBox = QMessageBox()
        msgBox.setText(r)
        msgBox.exec_()
    ###########################################################################    




















