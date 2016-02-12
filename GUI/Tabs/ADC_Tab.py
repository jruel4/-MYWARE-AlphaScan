# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:04:12 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

class ADC_REG_TAB( QWidget):
    def __init__(self, Device, parent=None):
        super(ADC_REG_TAB, self).__init__(parent)
        self._Device = Device
        
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
        self.rowDict = dict()
        self.rowDict[0]  = {'ADDRESS':QLabel('00h'), 'REGISTER':QLabel('ID'),          'DEFAULT':QLabel('00')}
        self.rowDict[1]  = {'ADDRESS':QLabel('01h'), 'REGISTER':QLabel('CONFIG_1'),    'DEFAULT':QLabel('96')}
        self.rowDict[2]  = {'ADDRESS':QLabel('02h'), 'REGISTER':QLabel('CONFIG_2'),    'DEFAULT':QLabel('C0')}
        self.rowDict[3]  = {'ADDRESS':QLabel('03h'), 'REGISTER':QLabel('CONFIG_3'),    'DEFAULT':QLabel('60')}
        self.rowDict[4]  = {'ADDRESS':QLabel('04h'), 'REGISTER':QLabel('LOFF'),        'DEFAULT':QLabel('00')}
        self.rowDict[5]  = {'ADDRESS':QLabel('05h'), 'REGISTER':QLabel('CH_1_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[6]  = {'ADDRESS':QLabel('06h'), 'REGISTER':QLabel('CH_2_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[7]  = {'ADDRESS':QLabel('07h'), 'REGISTER':QLabel('CH_3_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[8]  = {'ADDRESS':QLabel('08h'), 'REGISTER':QLabel('CH_4_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[9]  = {'ADDRESS':QLabel('09h'), 'REGISTER':QLabel('CH_5_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[10] = {'ADDRESS':QLabel('0Ah'), 'REGISTER':QLabel('CH_6_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[11] = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('CH_7_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[12] = {'ADDRESS':QLabel('0Ch'), 'REGISTER':QLabel('CH_8_Set'),    'DEFAULT':QLabel('61')}
        self.rowDict[13] = {'ADDRESS':QLabel('0Dh'), 'REGISTER':QLabel('BIAS_SENS_P'), 'DEFAULT':QLabel('00')}
        self.rowDict[14] = {'ADDRESS':QLabel('0Eh'), 'REGISTER':QLabel('BIAS_SENS_N'), 'DEFAULT':QLabel('00')}
        self.rowDict[15] = {'ADDRESS':QLabel('0Fh'), 'REGISTER':QLabel('LOFF_SENS_P'), 'DEFAULT':QLabel('00')}
        self.rowDict[16] = {'ADDRESS':QLabel('10h'), 'REGISTER':QLabel('LOFF_SENS_N'), 'DEFAULT':QLabel('00')}
        self.rowDict[17] = {'ADDRESS':QLabel('11h'), 'REGISTER':QLabel('LOFF_FLIP'),   'DEFAULT':QLabel('00')}
        self.rowDict[18] = {'ADDRESS':QLabel('12h'), 'REGISTER':QLabel('LOFF_STAT_P'), 'DEFAULT':QLabel('00')}
        self.rowDict[19] = {'ADDRESS':QLabel('13h'), 'REGISTER':QLabel('LOFF_STAT_N'), 'DEFAULT':QLabel('00')}
        self.rowDict[20] = {'ADDRESS':QLabel('14h'), 'REGISTER':QLabel('GPIO'),        'DEFAULT':QLabel('0F')}
        self.rowDict[21] = {'ADDRESS':QLabel('15h'), 'REGISTER':QLabel('MISC_1'),      'DEFAULT':QLabel('00')}
        self.rowDict[22] = {'ADDRESS':QLabel('16h'), 'REGISTER':QLabel('MISC_2'),      'DEFAULT':QLabel('00')}
        self.rowDict[23] = {'ADDRESS':QLabel('17h'), 'REGISTER':QLabel('CONFIG_4'),    'DEFAULT':QLabel('00')}    
        
        # Add checkboxes for each bit in register
        for i in range(len(self.rowDict)):
            for j in range(8):
                self.rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populat grid layout with widgets
        for i in range(len(self.rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(self.rowDict[i][colLabels[j]], i+1, j)

        # Connect check box signals to a slot which checks all registers against local map and updates appropo.
        for i in range(len(self.rowDict)):
            for j in range(8):
                self.rowDict[i]['BIT_'+str(j)].stateChanged.connect(self.update_registers)
                
        # Create local adc register map
        self.ADC_RegMap = [[False for i in range(8)] for j in range(24)] 
        
        # Set widget formatting
        ColLabelWidgets[0].setAutoFillBackground(True)
        p = ColLabelWidgets[0].palette()
        p.setColor(ColLabelWidgets[0].backgroundRole(), 'blue')
        ColLabelWidgets[0].setPalette(p)
        
        # Add Button_UpdateRegister
        self.Button_UpdateRegister = QPushButton("Update Registers")
        mainLayout.addWidget(self.Button_UpdateRegister)
        self.Button_UpdateRegister.clicked.connect(self.sync_registers_to_ads)
        
    @Slot()
    def sync_registers_to_ads(self):
        
        # TODO check to ensure that (not streaming) and (connected)
        self.ADC_RegMap = self._Device.sync_adc_registers()
        
        # set all check boxes to match RegMap
        for i in range(len(self.rowDict)):
            for j in range(8):
                if self.ADC_RegMap[i][j]:
                    self.rowDict[i]['BIT_'+str(j)].setCheckState(Qt.CheckState.Checked)
                else:
                    self.rowDict[i]['BIT_'+str(j)].setCheckState(Qt.CheckState.Unchecked)
    
    @Slot()
    def update_registers(self):
        #TODO abort if not connected or is streaming
        reg_to_update = list()
        for i in range(len(self.rowDict)):
            for j in range(8):
                if self.rowDict[i]['BIT_'+str(j)].isChecked() != self.ADC_RegMap[i][j]:
                    reg_to_update += [(i,j)] #i=reg,j=bit
        if len(reg_to_update) > 0:
            self._Device.update_adc_registers(reg_to_update) #TODO add validation here
