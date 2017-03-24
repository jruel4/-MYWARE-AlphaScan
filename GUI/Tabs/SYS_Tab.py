# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 16:48:50 2016

@author: marzipan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 19:47:40 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

''' Test vispy code '''
#from vispy_plotter import Canvas

class SYS_TAB(QWidget):
    
    SIG_reserve_tcp_buffer = Signal()
    
    # Define Init Method
    def __init__(self, Device, Debug):
        super(SYS_TAB, self).__init__(None)
        
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
        #TODO self.layout.setColumnStretch(3,1)
        
        #######################################################################
        # Display system parameters
        #######################################################################
        
        self.Text_Vcc = QLabel("VCC: ")
        self.Text_FreeHeap = QLabel("Free Heap: ")
        self.Text_ChipId = QLabel("Chip ID: ")
        self.Text_SdkVer = QLabel("SDK Version: ")
        self.Text_BootVer = QLabel("Boot Version: ")
        self.Text_BootMode = QLabel("Boot Mode: ")
        self.Text_CpuFreq = QLabel("CPU Frequency (MHz): ")
        self.Text_FlashChipId = QLabel("Flash Chip ID: ")
        self.Text_FlashChipRealSize = QLabel("Flash Chip Real Size: ")
        self.Text_FlashChipSpeed = QLabel("Flash Chip Speed: ")
        self.Text_FlashChipMode = QLabel("Flash Chip Mode: ")
        self.Text_FlashChipSize = QLabel("Flash Chip Size: ")
        self.Text_FreeSketchSpace = QLabel("Free Sketch Space: ")
        
        self.Text_VccVAL = QLabel("")
        self.Text_FreeHeapVAL = QLabel("")
        self.Text_ChipIdVAL = QLabel("")
        self.Text_SdkVerVAL = QLabel("")
        self.Text_BootVerVAL = QLabel("")
        self.Text_BootModeVAL = QLabel("")
        self.Text_CpuFreqVAL = QLabel("")
        self.Text_FlashChipIdVAL = QLabel("")
        self.Text_FlashChipRealSizeVAL = QLabel("")
        self.Text_FlashChipSpeedVAL = QLabel("")
        self.Text_FlashChipModeVAL = QLabel("")
        self.Text_FlashChipSizeVAL = QLabel("")
        self.Text_FreeSketchSpaceVAL = QLabel("")
        
        self.layout.addWidget(self.Text_Vcc, 0, 0)
        self.layout.addWidget(self.Text_FreeHeap, 1, 0)
        self.layout.addWidget(self.Text_ChipId, 2, 0)
        self.layout.addWidget(self.Text_SdkVer, 3, 0)
        self.layout.addWidget(self.Text_BootVer, 4, 0)
        self.layout.addWidget(self.Text_BootMode, 5, 0)
        self.layout.addWidget(self.Text_CpuFreq, 6, 0)
        self.layout.addWidget(self.Text_FlashChipId, 7, 0)
        self.layout.addWidget(self.Text_FlashChipRealSize, 8, 0)
        self.layout.addWidget(self.Text_FlashChipSpeed, 9, 0)
        self.layout.addWidget(self.Text_FlashChipMode, 10, 0)
        self.layout.addWidget(self.Text_FlashChipSize, 11, 0)
        self.layout.addWidget(self.Text_FreeSketchSpace, 12, 0)
        
        self.layout.addWidget(self.Text_VccVAL, 0, 1)
        self.layout.addWidget(self.Text_FreeHeapVAL, 1, 1)
        self.layout.addWidget(self.Text_ChipIdVAL, 2, 1)
        self.layout.addWidget(self.Text_SdkVerVAL, 3, 1)
        self.layout.addWidget(self.Text_BootVerVAL, 4, 1)
        self.layout.addWidget(self.Text_BootModeVAL, 5, 1)
        self.layout.addWidget(self.Text_CpuFreqVAL, 6, 1)
        self.layout.addWidget(self.Text_FlashChipIdVAL, 7, 1)
        self.layout.addWidget(self.Text_FlashChipRealSizeVAL, 8, 1)
        self.layout.addWidget(self.Text_FlashChipSpeedVAL, 9, 1)
        self.layout.addWidget(self.Text_FlashChipModeVAL, 10, 1)
        self.layout.addWidget(self.Text_FlashChipSizeVAL, 11, 1)
        self.layout.addWidget(self.Text_FreeSketchSpaceVAL, 12, 1)
        
#==============================================================================
#         fig = Canvas()
#         self.layout.addWidget(fig.native, 13,1)
#==============================================================================
        
        #######################################################################
        # Add control buttons
        #######################################################################
        
        self.Button_RequestSysParams = QPushButton("Request System MCU Parameters")
        self.Button_RefreshDisplay = QPushButton("Refresh Displayed Paramters")
        
        self.layout.addWidget(self.Button_RequestSysParams, 13, 0)
        self.layout.addWidget(self.Button_RefreshDisplay, 14, 0)
        
        self.Button_RequestSysParams.clicked.connect(self.request_sys_params)
        self.Button_RefreshDisplay.clicked.connect(self.refresh_display)
        
    @Slot()
    def request_sys_params(self):
        # Disable auto-connect as it interferes with param retrieval
        self.SIG_reserve_tcp_buffer.emit()
        # Execute device command
        r = self._Device.generic_tcp_command_BYTE("GEN_get_sys_params")
        msg = QMessageBox()
        msg.setText(r)
        msg.exec_()
        #TODO maybe add 1 second interval display, or add tcp size check update loop?  
    
    @Slot()
    def refresh_display(self):
        if self._Device.parse_sys_commands():
            self.Text_VccVAL.setText(self._Device.SysParams["vcc"])
            self.Text_FreeHeapVAL.setText(self._Device.SysParams["free_heap"])
            self.Text_ChipIdVAL.setText(self._Device.SysParams["mcu_chip_id"])
            self.Text_SdkVerVAL.setText(self._Device.SysParams["sdk_ver"])
            self.Text_BootVerVAL.setText(self._Device.SysParams["boot_ver"]) 
            self.Text_BootModeVAL.setText(self._Device.SysParams["boot_mode"]) 
            self.Text_CpuFreqVAL.setText(self._Device.SysParams["cpu_freq_mhz"])
            self.Text_FlashChipIdVAL.setText(self._Device.SysParams["flash_chip_id"])
            self.Text_FlashChipRealSizeVAL.setText(self._Device.SysParams["flash_chip_real_size"])
            self.Text_FlashChipSpeedVAL.setText(self._Device.SysParams["flash_chip_speed"])
            self.Text_FlashChipModeVAL.setText(self._Device.SysParams["flash_chip_mode"])
            self.Text_FlashChipSizeVAL.setText(self._Device.SysParams["flash_chip_size"])
            self.Text_FreeSketchSpaceVAL.setText(self._Device.SysParams["free_sketch_space"])
        else:
            msg = QMessageBox()
            msg.setText("Did not find complete response in buffer")
            msg.exec_()
        
        
        





















