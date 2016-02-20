# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 14:04:30 2016

@author: marzipan
"""

from PySide.QtCore import *
from PySide.QtGui import *

class ACCEL_REG_TAB( QWidget):
    def __init__(self, Device, parent=None):
        super(ACCEL_REG_TAB, self).__init__(parent)
        
        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        container = QWidget()
        # Create and set grid layout
        mainLayout =  QGridLayout()

        scrollArea.setWidget(container)        
        container.setLayout(mainLayout)
        
        # Set layout formatting
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setColumnStretch(10,1)

        # Define column labels
        colLabels = ['ADDRESS', 'REGISTER', 'DEFAULT', 'BIT_7', 'BIT_6', 'BIT_5', 'BIT_4', 'BIT_3', 'BIT_2', 'BIT_1', 'BIT_0', ]

        # Create label row
        for i in range(len(colLabels)):
            mainLayout.addWidget(QLabel(colLabels[i]), 0, i)
        
        # Populate labels row by row
        self.rowDict = dict()
        self.rowDict[0]  = {'ADDRESS':QLabel('0Bh'), 'REGISTER':QLabel('TEMP_L'),    'DEFAULT':QLabel('OUT')}
        self.rowDict[1]  = {'ADDRESS':QLabel('0Ch'), 'REGISTER':QLabel('TEMP_H'),    'DEFAULT':QLabel('OUT')}
        self.rowDict[2]  = {'ADDRESS':QLabel('0Eh'), 'REGISTER':QLabel('RESERVED'),  'DEFAULT':QLabel('OUT')}
        self.rowDict[3]  = {'ADDRESS':QLabel('0Fh'), 'REGISTER':QLabel('WHO_AM_I'),  'DEFAULT':QLabel('01000001')}
        self.rowDict[4]  = {'ADDRESS':QLabel('1Eh'), 'REGISTER':QLabel('ACT_THS'),   'DEFAULT':QLabel('00000000')}
        self.rowDict[5]  = {'ADDRESS':QLabel('1Fh'), 'REGISTER':QLabel('ACT_DUR'),   'DEFAULT':QLabel('00000000')}
        self.rowDict[6]  = {'ADDRESS':QLabel('20h'), 'REGISTER':QLabel('CTRL_1'),    'DEFAULT':QLabel('00000111')}
        self.rowDict[7]  = {'ADDRESS':QLabel('21h'), 'REGISTER':QLabel('CTRL_2'),    'DEFAULT':QLabel('00000000')}
        self.rowDict[8]  = {'ADDRESS':QLabel('22h'), 'REGISTER':QLabel('CTRL_3'),    'DEFAULT':QLabel('00000000')}
        self.rowDict[9]  = {'ADDRESS':QLabel('23h'), 'REGISTER':QLabel('CTRL_4'),    'DEFAULT':QLabel('00000100')}
        self.rowDict[10] = {'ADDRESS':QLabel('24h'), 'REGISTER':QLabel('CTRL_5'),    'DEFAULT':QLabel('00000000')}
        self.rowDict[11] = {'ADDRESS':QLabel('25h'), 'REGISTER':QLabel('CTRL_6'),    'DEFAULT':QLabel('00000000')}
        self.rowDict[12] = {'ADDRESS':QLabel('26h'), 'REGISTER':QLabel('CTRL_7'),    'DEFAULT':QLabel('00000000')}
        self.rowDict[13] = {'ADDRESS':QLabel('27h'), 'REGISTER':QLabel('STATUS'),    'DEFAULT':QLabel('OUT')}
        self.rowDict[14] = {'ADDRESS':QLabel('28h'), 'REGISTER':QLabel('OUT_X_L'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[15] = {'ADDRESS':QLabel('29h'), 'REGISTER':QLabel('OUT_X_H'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[16] = {'ADDRESS':QLabel('2Ah'), 'REGISTER':QLabel('OUT_Y_L'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[17] = {'ADDRESS':QLabel('2Bh'), 'REGISTER':QLabel('OUT_Y_H'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[18] = {'ADDRESS':QLabel('2Ch'), 'REGISTER':QLabel('OUT_Z_L'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[19] = {'ADDRESS':QLabel('2Dh'), 'REGISTER':QLabel('OUT_Z_H'),   'DEFAULT':QLabel('OUT')}
        self.rowDict[20] = {'ADDRESS':QLabel('2Eh'), 'REGISTER':QLabel('FIFO_CTRL'), 'DEFAULT':QLabel('00000000')}
        self.rowDict[21] = {'ADDRESS':QLabel('2Fh'), 'REGISTER':QLabel('FIFO_SRC'),  'DEFAULT':QLabel('OUT')}
        self.rowDict[22] = {'ADDRESS':QLabel('30h'), 'REGISTER':QLabel('IG_CFG_1'),  'DEFAULT':QLabel('00000000')}
        self.rowDict[23] = {'ADDRESS':QLabel('31h'), 'REGISTER':QLabel('IG_SRC_1'),  'DEFAULT':QLabel('OUT')}    
        self.rowDict[24] = {'ADDRESS':QLabel('32h'), 'REGISTER':QLabel('IG_THS_X1'), 'DEFAULT':QLabel('00000000')}   
        self.rowDict[25] = {'ADDRESS':QLabel('33h'), 'REGISTER':QLabel('IG_THS_Y1'), 'DEFAULT':QLabel('00000000')}   
        self.rowDict[26] = {'ADDRESS':QLabel('34h'), 'REGISTER':QLabel('IG_THS_Z1'), 'DEFAULT':QLabel('00000000')}   
        self.rowDict[27] = {'ADDRESS':QLabel('35h'), 'REGISTER':QLabel('IG_DUR_1'),  'DEFAULT':QLabel('00000000')}   
        self.rowDict[28] = {'ADDRESS':QLabel('36h'), 'REGISTER':QLabel('IG_CGF_2'),  'DEFAULT':QLabel('00000000')}   
        self.rowDict[29] = {'ADDRESS':QLabel('37h'), 'REGISTER':QLabel('IG_SRC_2'),  'DEFAULT':QLabel('OUT')}   
        self.rowDict[30] = {'ADDRESS':QLabel('38h'), 'REGISTER':QLabel('IG_THS_2'),  'DEFAULT':QLabel('00000000')}   
        self.rowDict[31] = {'ADDRESS':QLabel('39h'), 'REGISTER':QLabel('IG_DUR_2'),  'DEFAULT':QLabel('00000000')}   
        self.rowDict[32] = {'ADDRESS':QLabel('3Ah'), 'REGISTER':QLabel('XL_REF'),    'DEFAULT':QLabel('00000000')}   
        self.rowDict[33] = {'ADDRESS':QLabel('3Bh'), 'REGISTER':QLabel('XH_REF'),    'DEFAULT':QLabel('00000000')}   
        self.rowDict[34] = {'ADDRESS':QLabel('3Ch'), 'REGISTER':QLabel('YL_REF'),    'DEFAULT':QLabel('00000000')}   
        self.rowDict[35] = {'ADDRESS':QLabel('3Dh'), 'REGISTER':QLabel('YH_REF'),    'DEFAULT':QLabel('00000000')}   
        self.rowDict[36] = {'ADDRESS':QLabel('3Eh'), 'REGISTER':QLabel('ZL_REF'),    'DEFAULT':QLabel('00000000')}  
        self.rowDict[37] = {'ADDRESS':QLabel('3Fh'), 'REGISTER':QLabel('ZH_REF'),    'DEFAULT':QLabel('00000000')}  
        
        # Add checkboxes for each bit in register
        for i in range(len(self.rowDict)):
            for j in range(8):
                self.rowDict[i]['BIT_'+str(j)] = QCheckBox()
            
        # Populate grid layout with widgets
        for i in range(len(self.rowDict)):
            for j in range(len(colLabels)):
                mainLayout.addWidget(self.rowDict[i][colLabels[j]], i+1, j)
                
        # Limit height
        #self.setMaximumHeight(200)

