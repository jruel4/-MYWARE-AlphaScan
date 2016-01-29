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
from AlphaScanController import AlphaScanDevice
import time

try:
    qt_app = QApplication(sys.argv)
except: # could fail for reasons other than already exists... 
    pass

class AlphaScanGui(QWidget): #TODO probably want something other than dialog here
    def __init__(self, Device, fileName, parent=None):
        super(AlphaScanGui, self).__init__(parent)
        
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
        self.StreamingStatus = QLabel("Not Streaming")
        self.ConnectionStatus = QLabel("Not Connected")
        
        statusArea.addWidget(self.StreamingStatus)
        statusArea.addWidget(self.ConnectionStatus)
        
        # Create tabs
        tabWidget.addTab(GeneralTab(Device), "General")
        tabWidget.addTab(ADC_REG_TAB(), "ADC")
        tabWidget.addTab(PWR_REG_TAB(), "Power")
        tabWidget.addTab(ACCEL_REG_TAB(), "Accel")

        self.setWindowTitle("AlphaScan Controller")
        
    def run(self):
        # Show the form
        self.show()
        # Run the qt application
        qt_app.exec_()

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
        
        
    ###########################################################################
    # Slots ###################################################################
    ###########################################################################
        
    @Slot()
    def connect_to_device(self):
        if self.Connected: return
        self.Text_ConnectStatus.setText("Connecting to AlphaScan...")
        if self._Device.init_TCP():
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
        accel_status_string = self._Device.get_accel_status()
        self.Text_AccelStatus.setText(accel_status_string)
        
    @Slot()
    def update_power_status(self):
        if self.Streaming or not self.Connected:
            self.Text_PowerStatus.setText("ILLEGAL")
            return
        power_status_string = self._Device.get_power_status()
        self.Text_PowerStatus.setText(power_status_string)
        
    @Slot()
    def update_adc_status(self):
        if self.Streaming or not self.Connected:
            self.Text_PowerStatus.setText("ILLEGAL")
            return
        adc_status_string = self._Device.get_adc_status()
        self.Text_AdcStatus.setText(adc_status_string)
    
    @Slot()
    def begin_streaming(self):
        if self.Streaming or not self.Connected:
            return
        begin_stream_string = self._Device.initiate_UDP_stream()
        self.Streaming = True # TODO validate
        self.Text_AdcStreamStatus.setText(begin_stream_string)
    
    @Slot()
    def stop_streaming(self):
        if not self.Streaming or not self.Connected:
            return
        end_stream_string = self._Device.terminate_UDP_stream()
        self.Streaming = False # TODO validate
        self.Text_AdcStreamStatus.setText(end_stream_string)
        
    ###########################################################################    
        
    def closeEvent(self, event):
        self._Device.close_TCP()
        self._Device.close_UDP()
        event.accept()

#TODO replace permission tab
class ADC_REG_TAB( QWidget):
    def __init__(self, parent=None):
        super(ADC_REG_TAB, self).__init__(parent)

        # Create and set grid layout
        mainLayout =  QGridLayout()        
        self.setLayout(mainLayout)
        
        # Set layout formatting
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setColumnStretch(10,1)
        
        # Define column labels
        colLabels = ['ADDRESS', 'REGISTER', 'DEFAULT', 'BIT_7', 'BIT_6', 'BIT_5', 'BIT_4', 'BIT_3', 'BIT_2', 'BIT_1', 'BIT_0', ]

        # Create label rows
        ColLabelWidgets = list()
        for l in colLabels:
            ColLabelWidgets += [QLabel(l)]
        for i in range(len(colLabels)):
            mainLayout.addWidget(ColLabelWidgets[i], 0, i)
        
        # Populate labels row by row
        rowDict = dict()
        rowDict[0]  = {'ADDRESS':QLabel('00h'), 'REGISTER':QLabel('ID'),          'DEFAULT':QLabel('00')}
        rowDict[1]  = {'ADDRESS':QLabel('01h'), 'REGISTER':QLabel('CONFIG_1'),    'DEFAULT':QLabel('96')}
        rowDict[2]  = {'ADDRESS':QLabel('02h'), 'REGISTER':QLabel('CONFIG_2'),    'DEFAULT':QLabel('C0')}
        rowDict[3]  = {'ADDRESS':QLabel('03h'), 'REGISTER':QLabel('CONFIG_3'),    'DEFAULT':QLabel('60')}
        rowDict[4]  = {'ADDRESS':QLabel('04h'), 'REGISTER':QLabel('LOFF'),        'DEFAULT':QLabel('00')}
        rowDict[5]  = {'ADDRESS':QLabel('05h'), 'REGISTER':QLabel('CH_1_Set'),    'DEFAULT':QLabel('61')}
        rowDict[6]  = {'ADDRESS':QLabel('06h'), 'REGISTER':QLabel('CH_2_Set'),    'DEFAULT':QLabel('61')}
        rowDict[7]  = {'ADDRESS':QLabel('07h'), 'REGISTER':QLabel('CH_3_Set'),    'DEFAULT':QLabel('61')}
        rowDict[8]  = {'ADDRESS':QLabel('08h'), 'REGISTER':QLabel('CH_4_Set'),    'DEFAULT':QLabel('61')}
        rowDict[9]  = {'ADDRESS':QLabel('09h'), 'REGISTER':QLabel('CH_5_Set'),    'DEFAULT':QLabel('61')}
        rowDict[10] = {'ADDRESS':QLabel('0Ah'), 'REGISTER':QLabel('CH_6_Set'),    'DEFAULT':QLabel('61')}
        rowDict[11] = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('CH_7_Set'),    'DEFAULT':QLabel('61')}
        rowDict[12] = {'ADDRESS':QLabel('0Ch'), 'REGISTER':QLabel('CH_8_Set'),    'DEFAULT':QLabel('61')}
        rowDict[13] = {'ADDRESS':QLabel('0Dh'), 'REGISTER':QLabel('BIAS_SENS_P'), 'DEFAULT':QLabel('00')}
        rowDict[14] = {'ADDRESS':QLabel('0Eh'), 'REGISTER':QLabel('BIAS_SENS_N'), 'DEFAULT':QLabel('00')}
        rowDict[15] = {'ADDRESS':QLabel('0Fh'), 'REGISTER':QLabel('LOFF_SENS_P'), 'DEFAULT':QLabel('00')}
        rowDict[16] = {'ADDRESS':QLabel('10h'), 'REGISTER':QLabel('LOFF_SENS_N'), 'DEFAULT':QLabel('00')}
        rowDict[17] = {'ADDRESS':QLabel('11h'), 'REGISTER':QLabel('LOFF_FLIP'),   'DEFAULT':QLabel('00')}
        rowDict[18] = {'ADDRESS':QLabel('12h'), 'REGISTER':QLabel('LOFF_STAT_P'), 'DEFAULT':QLabel('00')}
        rowDict[19] = {'ADDRESS':QLabel('13h'), 'REGISTER':QLabel('LOFF_STAT_N'), 'DEFAULT':QLabel('00')}
        rowDict[20] = {'ADDRESS':QLabel('14h'), 'REGISTER':QLabel('GPIO'),        'DEFAULT':QLabel('0F')}
        rowDict[21] = {'ADDRESS':QLabel('15h'), 'REGISTER':QLabel('MISC_1'),      'DEFAULT':QLabel('00')}
        rowDict[22] = {'ADDRESS':QLabel('16h'), 'REGISTER':QLabel('MISC_2'),      'DEFAULT':QLabel('00')}
        rowDict[23] = {'ADDRESS':QLabel('17h'), 'REGISTER':QLabel('CONFIG_4'),    'DEFAULT':QLabel('00')}    
        
        # Add checkboxes for each bit in register
        for i in range(len(rowDict)):
            for j in range(8):
                rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populat grid layout with widgets
        for i in range(len(rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(rowDict[i][colLabels[j]], i+1, j)
                
        # Set widget formatting
        ColLabelWidgets[0].setAutoFillBackground(True)
        p = ColLabelWidgets[0].palette()
        p.setColor(ColLabelWidgets[0].backgroundRole(), 'blue')
        ColLabelWidgets[0].setPalette(p)



class PWR_REG_TAB( QWidget):
    def __init__(self, parent=None):
        super(PWR_REG_TAB, self).__init__(parent)

        # Create and set grid layout
        mainLayout =  QGridLayout()        
        self.setLayout(mainLayout)
        
        # Set layout formatting
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setColumnStretch(10,1)

        # Define column labels
        colLabels = ['ADDRESS', 'REGISTER', 'DEFAULT', 'BIT_7', 'BIT_6', 'BIT_5', 'BIT_4', 'BIT_3', 'BIT_2', 'BIT_1', 'BIT_0', ]

        # Create label row
        for i in range(len(colLabels)):
            mainLayout.addWidget(QLabel(colLabels[i]), 0, i)
        
        # Populate labels row by row
        rowDict = dict()
        rowDict[0]  = {'ADDRESS':QLabel('00h'), 'REGISTER':QLabel('STATUS'),      'DEFAULT':QLabel('00000000')}
        rowDict[1]  = {'ADDRESS':QLabel('01h'), 'REGISTER':QLabel('FAULT'),       'DEFAULT':QLabel('00000000')}
        rowDict[2]  = {'ADDRESS':QLabel('02h'), 'REGISTER':QLabel('TS_Control'),  'DEFAULT':QLabel('10001000')}
        rowDict[3]  = {'ADDRESS':QLabel('03h'), 'REGISTER':QLabel('Fast_Charge'), 'DEFAULT':QLabel('00010100')}
        rowDict[4]  = {'ADDRESS':QLabel('04h'), 'REGISTER':QLabel('TERMIN'),      'DEFAULT':QLabel('00001110')}
        rowDict[5]  = {'ADDRESS':QLabel('05h'), 'REGISTER':QLabel('Bat_Vol'),     'DEFAULT':QLabel('01111000')}
        rowDict[6]  = {'ADDRESS':QLabel('06h'), 'REGISTER':QLabel('Sys_Vout'),    'DEFAULT':QLabel('10101010')}
        rowDict[7]  = {'ADDRESS':QLabel('07h'), 'REGISTER':QLabel('Load_Sw'),     'DEFAULT':QLabel('01111100')}
        rowDict[8]  = {'ADDRESS':QLabel('08h'), 'REGISTER':QLabel('Push_Btn'),    'DEFAULT':QLabel('01101000')}
        rowDict[9]  = {'ADDRESS':QLabel('09h'), 'REGISTER':QLabel('ILIM'),        'DEFAULT':QLabel('00001010')}
        rowDict[10] = {'ADDRESS':QLabel('0Ah'), 'REGISTER':QLabel('Bat_Mon'),     'DEFAULT':QLabel('00000000')}
        rowDict[11] = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('Vin_DPM'),     'DEFAULT':QLabel('01001010')}   
        
        # Add checkboxes for each bit in register
        for i in range(len(rowDict)):
            for j in range(8):
                rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populat grid layout with widgets
        for i in range(len(rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(rowDict[i][colLabels[j]], i+1, j)

class ACCEL_REG_TAB( QWidget):
    def __init__(self, parent=None):
        super(ACCEL_REG_TAB, self).__init__(parent)

        # Create and set grid layout
        mainLayout =  QGridLayout()        
        self.setLayout(mainLayout)
        
        # Set layout formatting
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setColumnStretch(10,1)

        # Define column labels
        colLabels = ['ADDRESS', 'REGISTER', 'DEFAULT', 'BIT_7', 'BIT_6', 'BIT_5', 'BIT_4', 'BIT_3', 'BIT_2', 'BIT_1', 'BIT_0', ]

        # Create label row
        for i in range(len(colLabels)):
            mainLayout.addWidget(QLabel(colLabels[i]), 0, i)
        
        # Populate labels row by row
        rowDict = dict()
        rowDict[0]  = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('TEMP_L'),    'DEFAULT':QLabel('OUT')}
        rowDict[1]  = {'ADDRESS':QLabel('0Ch'), 'REGISTER':QLabel('TEMP_H'),    'DEFAULT':QLabel('OUT')}
        rowDict[2]  = {'ADDRESS':QLabel('0Eh'), 'REGISTER':QLabel('RESERVED'),  'DEFAULT':QLabel('OUT')}
        rowDict[3]  = {'ADDRESS':QLabel('0Fh'), 'REGISTER':QLabel('WHO_AM_I'),  'DEFAULT':QLabel('01000001')}
        rowDict[4]  = {'ADDRESS':QLabel('1Eh'), 'REGISTER':QLabel('ACT_THS'),   'DEFAULT':QLabel('00000000')}
        rowDict[5]  = {'ADDRESS':QLabel('1Fh'), 'REGISTER':QLabel('ACT_DUR'),   'DEFAULT':QLabel('00000000')}
        rowDict[6]  = {'ADDRESS':QLabel('20h'), 'REGISTER':QLabel('CTRL_1'),    'DEFAULT':QLabel('00000111')}
        rowDict[7]  = {'ADDRESS':QLabel('21h'), 'REGISTER':QLabel('CTRL_2'),    'DEFAULT':QLabel('00000000')}
        rowDict[8]  = {'ADDRESS':QLabel('22h'), 'REGISTER':QLabel('CTRL_3'),    'DEFAULT':QLabel('00000000')}
        rowDict[9]  = {'ADDRESS':QLabel('23h'), 'REGISTER':QLabel('CTRL_4'),    'DEFAULT':QLabel('00000100')}
        rowDict[10] = {'ADDRESS':QLabel('24h'), 'REGISTER':QLabel('CTRL_5'),    'DEFAULT':QLabel('00000000')}
        rowDict[11] = {'ADDRESS':QLabel('25h'), 'REGISTER':QLabel('CTRL_6'),    'DEFAULT':QLabel('00000000')}
        rowDict[12] = {'ADDRESS':QLabel('26h'), 'REGISTER':QLabel('CTRL_7'),    'DEFAULT':QLabel('00000000')}
        rowDict[13] = {'ADDRESS':QLabel('27h'), 'REGISTER':QLabel('STATUS'),    'DEFAULT':QLabel('OUT')}
        rowDict[14] = {'ADDRESS':QLabel('28h'), 'REGISTER':QLabel('OUT_X_L'),   'DEFAULT':QLabel('OUT')}
        rowDict[15] = {'ADDRESS':QLabel('29h'), 'REGISTER':QLabel('OUT_X_H'),   'DEFAULT':QLabel('OUT')}
        rowDict[16] = {'ADDRESS':QLabel('2Ah'), 'REGISTER':QLabel('OUT_Y_L'),   'DEFAULT':QLabel('OUT')}
        rowDict[17] = {'ADDRESS':QLabel('2Bh'), 'REGISTER':QLabel('OUT_Y_H'),   'DEFAULT':QLabel('OUT')}
        rowDict[18] = {'ADDRESS':QLabel('2Ch'), 'REGISTER':QLabel('OUT_Z_L'),   'DEFAULT':QLabel('OUT')}
        rowDict[19] = {'ADDRESS':QLabel('2Dh'), 'REGISTER':QLabel('OUT_Z_H'),   'DEFAULT':QLabel('OUT')}
        rowDict[20] = {'ADDRESS':QLabel('2Eh'), 'REGISTER':QLabel('FIFO_CTRL'), 'DEFAULT':QLabel('00000000')}
        rowDict[21] = {'ADDRESS':QLabel('2Fh'), 'REGISTER':QLabel('FIFO_SRC'),  'DEFAULT':QLabel('OUT')}
        rowDict[22] = {'ADDRESS':QLabel('30h'), 'REGISTER':QLabel('IG_CFG_1'),  'DEFAULT':QLabel('00000000')}
        rowDict[23] = {'ADDRESS':QLabel('31h'), 'REGISTER':QLabel('IG_SRC_1'),  'DEFAULT':QLabel('OUT')}    
        rowDict[24] = {'ADDRESS':QLabel('32h'), 'REGISTER':QLabel('IG_THS_X1'), 'DEFAULT':QLabel('00000000')}   
        rowDict[25] = {'ADDRESS':QLabel('33h'), 'REGISTER':QLabel('IG_THS_Y1'), 'DEFAULT':QLabel('00000000')}   
        rowDict[26] = {'ADDRESS':QLabel('34h'), 'REGISTER':QLabel('IG_THS_Z1'), 'DEFAULT':QLabel('00000000')}   
        rowDict[27] = {'ADDRESS':QLabel('35h'), 'REGISTER':QLabel('IG_DUR_1'),  'DEFAULT':QLabel('00000000')}   
        rowDict[28] = {'ADDRESS':QLabel('36h'), 'REGISTER':QLabel('IG_CGF_2'),  'DEFAULT':QLabel('00000000')}   
        rowDict[29] = {'ADDRESS':QLabel('37h'), 'REGISTER':QLabel('IG_SRC_2'),  'DEFAULT':QLabel('OUT')}   
        rowDict[30] = {'ADDRESS':QLabel('38h'), 'REGISTER':QLabel('IG_THS_2'),  'DEFAULT':QLabel('00000000')}   
        rowDict[31] = {'ADDRESS':QLabel('39h'), 'REGISTER':QLabel('IG_DUR_2'),  'DEFAULT':QLabel('00000000')}   
        rowDict[32] = {'ADDRESS':QLabel('3Ah'), 'REGISTER':QLabel('XL_REF'),    'DEFAULT':QLabel('00000000')}   
        rowDict[33] = {'ADDRESS':QLabel('3Bh'), 'REGISTER':QLabel('XH_REF'),    'DEFAULT':QLabel('00000000')}   
        rowDict[34] = {'ADDRESS':QLabel('3Ch'), 'REGISTER':QLabel('YL_REF'),    'DEFAULT':QLabel('00000000')}   
        rowDict[35] = {'ADDRESS':QLabel('3Dh'), 'REGISTER':QLabel('YH_REF'),    'DEFAULT':QLabel('00000000')}   
        rowDict[36] = {'ADDRESS':QLabel('3Eh'), 'REGISTER':QLabel('ZL_REF'),    'DEFAULT':QLabel('00000000')}  
        rowDict[37] = {'ADDRESS':QLabel('3Fh'), 'REGISTER':QLabel('ZH_REF'),    'DEFAULT':QLabel('00000000')}  
        
        # Add checkboxes for each bit in register
        for i in range(len(rowDict)):
            for j in range(8):
                rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populat grid layout with widgets
        for i in range(len(rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(rowDict[i][colLabels[j]], i+1, j)




###############################################################################
# RUN APPLICATION #############################################################
###############################################################################


import sys



if len(sys.argv) >= 2:
    fileName = sys.argv[1]
else:
    fileName = "."
    
# Run app     
# TODO rehash this with new class layout
dev = AlphaScanDevice() 
app = AlphaScanGui(dev, fileName)
time.sleep(0.01)
app.run()
            
           
# TODO troubleshoot timing issue on crashed startup - add delays before key points       
       
       
       
       
       
       
