# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:06:33 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *
from TimeSync import TimeSync
import time

class GeneralTab(QWidget):
    
    # Define Init Method
    def __init__(self,Device, Debug):
        super(GeneralTab, self).__init__(None)
        
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        self._Device = Device      
        self._Debug = Debug
        
        # Define status vars
        self.Connected = False
        self.Streaming = False
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        #TODO self.layout.setColumnStretch(3,1)
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
        
        self.Button_AdcBeginStream.clicked.connect(self.begin_streaming_tcp)
        self.Button_AdcStopStream.clicked.connect(self.stop_streaming)
        
        #######################################################################
        # General Message Area ################################################
        #######################################################################
        
        # Create general message label
        self.Text_GeneralMessage = QLabel("")
        self.layout.addWidget(self.Text_GeneralMessage, 5,0,1,2)
        
        # Add message formatting
#==============================================================================
#         self.Text_GeneralMessage.setAutoFillBackground(True)
#         p = self.Text_GeneralMessage.palette()
#         p.setColor(self.Text_GeneralMessage.backgroundRole(), 'cyan')
#         self.Text_GeneralMessage.setPalette(p)
#==============================================================================
        
        # Add clear general message button
        self.Button_ClearGeneralMessage = QPushButton("Clear Message")
        self.layout.addWidget(self.Button_ClearGeneralMessage, 5,2,1,1)
        self.Button_ClearGeneralMessage.clicked.connect(self.clear_gen_msg)
        
        # Add time sync button
        self.Button_SyncTime = QPushButton("Sync Time")
        self.layout.addWidget(self.Button_SyncTime, 5,1,1,1)
        self.Button_SyncTime.clicked.connect(self.synchronize_time)
        
        self.Progress_SyncProgress = QProgressBar()
        #self.Progress_SyncProgress.setAutoFillBackground(True)
        self.layout.addWidget(self.Progress_SyncProgress, 5,0,1,1)
        
        self.fake_time = 0
        

        
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
        
        #######################################################################
        # Update UDP Delay Value ##############################################
        #######################################################################
        
        self.Line_UdpDelayVal = QLineEdit("1500")       
        self.Button_SetUdpDelayVal = QPushButton("Set UDP Delay")
        
        self.layout.addWidget(self.Line_UdpDelayVal, 13, 0)
        self.layout.addWidget(self.Button_SetUdpDelayVal, 13, 1)
        
        self.Button_SetUdpDelayVal.clicked.connect(self.update_udp_delay)
        
        #######################################################################
        # Reset Device ########################################################
        #######################################################################
        
        self.Button_ResetDevice = QPushButton("Reset Device")
        self.layout.addWidget(self.Button_ResetDevice, 14,0)
        self.Button_ResetDevice.clicked.connect(self.reset_device)
        
        #######################################################################
        # Auto Connect Enable #################################################
        #######################################################################
        
        self.Text_AutoConnectEnable = QLabel("Auto Connect Enable")
        self.Check_AutoConnectEnable = QCheckBox()
        self.Check_AutoConnectEnable.setCheckState(Qt.CheckState.Unchecked)
        
        self.layout.addWidget(self.Text_AutoConnectEnable, 15, 0)
        self.layout.addWidget(self.Check_AutoConnectEnable, 15, 1)      
        
        #######################################################################
        # Web Update Mode #####################################################
        #######################################################################
        
        self.Button_WebUpdateMode = QPushButton("Enter Web Update Mode")
        self.layout.addWidget(self.Button_WebUpdateMode, 16, 0, 1, 1)
        self.Button_WebUpdateMode.clicked.connect(self.enter_web_update_mode)
        
#==============================================================================
#         #######################################################################
#         # Style Selection #####################################################
#         #######################################################################
#         
#         self.styleComboBox = QComboBox()
#         # add styles from QStyleFactory
#         self.styleComboBox.addItems(QStyleFactory.keys())
#         # find current style
#         index = self.styleComboBox.findText(
#                     qApp.style().objectName(),
#                     Qt.MatchFixedString)
#         # set current style
#         self.styleComboBox.setCurrentIndex(index)
#         # set style change handler
#         self.styleComboBox.activated[str].connect(self.handleStyleChanged)
#         self.layout.addWidget(self.styleComboBox, 16, 0)
#==============================================================================
                
        #######################################################################
        # Debug logging enabled ###############################################
        #######################################################################
        
        self.Text_DebugLogEnable = QLabel("Debug Logging Enable")
        self.Check_DebugLogEnable = QCheckBox()
        self.Check_DebugLogEnable.setCheckState(Qt.CheckState.Unchecked)
        
        self.layout.addWidget(self.Text_DebugLogEnable, 17, 0)
        self.layout.addWidget(self.Check_DebugLogEnable, 17, 1) 
        
        self.Check_DebugLogEnable.stateChanged.connect(self.toggle_debug_state)
        
        #######################################################################
        # Create Auto Connect Timer ###########################################
        #######################################################################
        self.auto_conn_timer = QTimer()
        self.auto_conn_timer.timeout.connect(self.auto_connect)
        self.auto_conn_timer.start(100)
        self.heartbeatIntervalCounter = 0
        self.heartbeatFailCounter = 0
        
        #######################################################################
        # Create Debug Log Timer ##############################################
        #######################################################################
        self.debug_log_timer = QTimer()
        self.debug_log_timer.timeout.connect(self.read_debug_log)
        self.debug_log_timer.start(100)
        
    ###########################################################################
    # Slots ###################################################################
    ###########################################################################

    @Slot()    
    def handleStyleChanged(self, style):
        qApp.setStyle(style)
        
    @Slot()
    def connect_to_device(self):
        # TODO find out where this blocks!
        if self.Connected: return
        self.Text_ConnectStatus.setText("Connecting to AlphaScan...")
        if self._Device.connect_to_device():
            self.Connected = True
            self.Text_ConnectStatus.setText("Connected")
        else:
            self.Text_ConnectStatus.setText("Connection FAILED")
            msgBox = QMessageBox()
            msgBox.setText(\
            "Make sure AlphaScan is powered on and wait about 10 " +\
            "seconds for it to be allocated an IP Adress by your router. " +\
            "If AlphaScan fails to connect, to will switch to Software " +\
            "Access Point Mode")
            #TODO automatically check if AP signal is available.
            msgBox.exec_()
    
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
        if not self.Connected:
            self.Text_GeneralMessage.setText("ILLEGAL: Connected must be true")
            return
        begin_stream_string = self._Device.initiate_TCP_stream()
        self.Streaming = True # TODO validate
        self.Text_AdcStreamStatus.setText(begin_stream_string)
        
    @Slot()
    def begin_streaming_tcp(self):
        if self.Streaming or not self.Connected:
            self.Text_GeneralMessage.setText("ILLEGAL")
            return
        begin_stream_string = self._Device.initiate_TCP_stream()
        self.Streaming = True # TODO validate
        self.Text_AdcStreamStatus.setText(begin_stream_string)
        
    @Slot()
    def begin_streaming_tcpX(self):
        begin_stream_string = self._Device.initiate_TCP_streamX()
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
    def stop_streaming_tcp(self):
        if not self.Streaming or not self.Connected:
            self.Text_GeneralMessage.setText("ILLEGAL: Streaming must be true, Connected must be true")
            return
        self._Device.terminate_TCP_stream()
        self.Streaming = False # TODO validate
        self.Text_AdcStreamStatus.setText("Stopped streaming")
        
    @Slot()
    def stop_streaming_tcp_X(self):
        r = self._Device.getPdataSize()
        self.Text_AdcStreamStatus.setText("Size pData: "+str(r))
  
        
    @Slot()
    def clear_gen_msg(self):
        self.Text_GeneralMessage.setText("")
        
    @Slot()
    def enter_ota_mode(self):
        r = self._Device.generic_tcp_command_BYTE('GEN_start_ota') 
        msgBox = QMessageBox()
        if 'OTA' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText(r)
        msgBox.exec_()
        self.disconnect_from_device()
        
    @Slot()
    def enter_web_update_mode(self):
        r = self._Device.generic_tcp_command_BYTE('GEN_web_update') 
        msgBox = QMessageBox()
        if 'web_update' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText(r)
        msgBox.exec_()
        self.disconnect_from_device()
        
    @Slot()
    def enter_ap_mode(self):
        r = self._Device.generic_tcp_command_BYTE('GEN_start_ap') 
        msgBox = QMessageBox()
        if 'ap_mode' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText(r)
        msgBox.exec_()
        self.disconnect_from_device()
    
    @Slot()
    def update_command_map(self):
        r = self._Device.update_command_map()
        msgBox = QMessageBox()
        if 'map_command' in r:#TODO add response into firmware
            msgBox.setText("SUCCESS")
        else:
            msgBox.setText(r)
        msgBox.exec_()
        
    @Slot()
    def update_udp_delay(self):
        r = self._Device.set_udp_delay(int(self.Line_UdpDelayVal.text()))
        msgBox = QMessageBox()
        msgBox.setText(r)
        msgBox.exec_()
        
    @Slot()
    def reset_device(self):
        r = self._Device.generic_tcp_command_BYTE("GEN_reset_device")
        msgBox = QMessageBox()
        msgBox.setText(r)
        msgBox.exec_()
        self.disconnect_from_device()
        
    @Slot()
    def disable_auto_connect(self):
        self._Debug.append("Disabling auto connect to save tcp buffer response")
        self.Check_AutoConnectEnable.setCheckState(Qt.CheckState.Unchecked)
    
    @Slot()
    def auto_connect(self):
        if self.Check_AutoConnectEnable.isChecked() and not self.Streaming:
            if not self.Connected:
                # connect routine 
                if self._Device.listen_for_device_beacon():
                    self._Debug.append("Device found, attempting to connect...")
                    self.connect_to_device()
                else:
                    # TODO check for Access Point Availability
                    pass
            else:
                # hearbeat routine, send ALIVE? query, and if no answer then disconnect_from_device
                # TODO This has risk of colliding with user actions, consider using an IDLE flag
                if self.heartbeatIntervalCounter > 40: 
                    # reset counter and send alive query
                    self.heartbeatIntervalCounter = 0
                    r = self._Device.generic_tcp_command_BYTE("GEN_alive_query")
                    if "ALIVE_ACK" not in r:
                        self.heartbeatFailCounter += 1
                    else:
                        self.heartbeatFailCounter = 0
                        
                    if self.heartbeatFailCounter > 1:
                        self.disconnect_from_device()
                        self.heartbeatFailCounter = 0
                else:
                    self.heartbeatIntervalCounter += 1
                    
        elif self.Check_AutoConnectEnable.isChecked() and self.Streaming:
            #TODO check for stream validity
            pass
        
    @Slot()
    def read_debug_log(self):
        if self.Check_DebugLogEnable.isChecked() and self.Connected and not self.Streaming:
            r = self._Device.read_debug_port()
            if r:
                self._Debug.append(r)
    
    @Slot()
    def toggle_debug_state(self):
        if self.Check_DebugLogEnable.isChecked():
            if self._Device.open_debug_port():
                self._Debug.append("Debug Enabled")
            else:
                self._Debug.append("Debug Enable Failed")
        else:
            if self._Device.close_debug_port():
                self._Debug.append("Debug Disabled")
            else:
                self._Debug.append("Debug Disable Failed")
        
            
    @Slot()
    def synchronize_time(self):
        self._Debug.append("beginning sync")
        QMessageBox.information(self, "Synchronizing Time", "Please wait for time sync to complete...")
        
        self.time_begin = time.time()
        self.xt = QTimer()
        self.xt.timeout.connect(self.update_progress)
        self.xt.start(600)
        
        r = self._Device.time_sync()
        self._Debug.append(str(r))
        
    @Slot()
    def update_progress(self):
        self.fake_time += 1
        self.Progress_SyncProgress.setValue(self.fake_time)  
        
        # Check if all devices are finished
        finished = True
        for i,d in enumerate(self._Device.dev):
            s = d.ts.finished.is_set()
            #self._Debug.append(str(i)+" "+str(s))
            finished &= s
            
            
        if (finished):
            self.Progress_SyncProgress.setValue(100) 
            self.xt.stop()
            QMessageBox.information(self, "Sync Complete", "Done!")   
            r = []
            for i,d in enumerate(self._Device.dev):
                # Process
                r += [d.ts.process_offsets()]
            key = "[drift(uS/S), len_offsets, drift_reasonable]\n"
            QMessageBox.information(self, "Sync Results", key+str(r))
                



















