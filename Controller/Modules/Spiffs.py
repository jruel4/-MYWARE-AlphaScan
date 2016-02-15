# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 16:15:04 2016

@author: marzipan
"""

''' 
Serial Peripheral Interface Flash File System (SPIFFS) Controller
Enables the following functions:
    - format drive
    - view contents of key files
        - command map
        - network parameters
    - FSINFO viewer
        - total size
        - used 
        - block size
        - page size
        - max open files
        - max path length

SPIFFS controller should utilize generic control methods from main control class
'''

class SPIFFS:
    
    def __init__(self, Device):
        self._Device = Device
        
    def formatFs(self):
        pass
    
    def getNetworkParams(self):
        pass
    
    def getCommandMap(self):
        pass
    
    def getFsInfo(self):
        pass
