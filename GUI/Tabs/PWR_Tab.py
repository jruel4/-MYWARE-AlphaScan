# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:04:39 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

class PWR_REG_TAB( QWidget):
    def __init__(self, Device, Debug, parent=None):
        super(PWR_REG_TAB, self).__init__(parent)
        
        self._Debug = Debug
        
        # Create and set grid layout
        mainLayout =  QGridLayout()        
        self.setLayout(mainLayout)
        
        # Set layout formatting
        mainLayout.setAlignment(Qt.AlignTop)
        #TODO mainLayout.setColumnStretch(10,1)

        # Define column labels
        colLabels = ['ADDRESS', 'REGISTER', 'DEFAULT', 'BIT_7', 'BIT_6', 'BIT_5', 'BIT_4', 'BIT_3', 'BIT_2', 'BIT_1', 'BIT_0', ]

        # Create label row
        for i in range(len(colLabels)):
            mainLayout.addWidget(QLabel(colLabels[i]), 0, i)
        
        # Populate labels row by row
        self.rowDict = dict()
        self.rowDict[0]  = {'ADDRESS':QLabel('00h'), 'REGISTER':QLabel('STATUS'),      'DEFAULT':QLabel('00000000')}
        self.rowDict[1]  = {'ADDRESS':QLabel('01h'), 'REGISTER':QLabel('FAULT'),       'DEFAULT':QLabel('00000000')}
        self.rowDict[2]  = {'ADDRESS':QLabel('02h'), 'REGISTER':QLabel('TS_Control'),  'DEFAULT':QLabel('10001000')}
        self.rowDict[3]  = {'ADDRESS':QLabel('03h'), 'REGISTER':QLabel('Fast_Charge'), 'DEFAULT':QLabel('00010100')}
        self.rowDict[4]  = {'ADDRESS':QLabel('04h'), 'REGISTER':QLabel('TERMIN'),      'DEFAULT':QLabel('00001110')}
        self.rowDict[5]  = {'ADDRESS':QLabel('05h'), 'REGISTER':QLabel('Bat_Vol'),     'DEFAULT':QLabel('01111000')}
        self.rowDict[6]  = {'ADDRESS':QLabel('06h'), 'REGISTER':QLabel('Sys_Vout'),    'DEFAULT':QLabel('10101010')}
        self.rowDict[7]  = {'ADDRESS':QLabel('07h'), 'REGISTER':QLabel('Load_Sw'),     'DEFAULT':QLabel('01111100')}
        self.rowDict[8]  = {'ADDRESS':QLabel('08h'), 'REGISTER':QLabel('Push_Btn'),    'DEFAULT':QLabel('01101000')}
        self.rowDict[9]  = {'ADDRESS':QLabel('09h'), 'REGISTER':QLabel('ILIM'),        'DEFAULT':QLabel('00001010')}
        self.rowDict[10] = {'ADDRESS':QLabel('0Ah'), 'REGISTER':QLabel('Bat_Mon'),     'DEFAULT':QLabel('00000000')}
        self.rowDict[11] = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('Vin_DPM'),     'DEFAULT':QLabel('01001010')}   
        
        # Add checkboxes for each bit in register
        for i in range(len(self.rowDict)):
            for j in range(8):
                self.rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populat grid layout with widgets
        for i in range(len(self.rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(self.rowDict[i][colLabels[j]], i+1, j)

