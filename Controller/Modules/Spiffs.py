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
import time

class SPIFFS:
    
    def __init__(self, Device):
        self._Device = Device
        
    def formatFs(self):
        r = self._Device.generic_tcp_command_BYTE("FS_format_fs")
        time.sleep(0.01)
        r += self._Device.read_tcp()
        return r
    
    def getNetworkParams(self):
        r = self._Device.generic_tcp_command_BYTE("FS_get_net_params")
        time.sleep(0.01)
        r += self._Device.read_tcp()
        return r
        
    def getCommandMap(self):
        r = self._Device.generic_tcp_command_BYTE("FS_get_command_map")
        if 'no_response' in r:
            r = 'Please read buff in a moment'
        return r
        
    def getFsInfo(self):
        r = self._Device.generic_tcp_command_BYTE("FS_get_fs_info")
        time.sleep(0.01)
        r += self._Device.read_tcp()
        return r
        
    def readTcpBuff(self):
        return self._Device.read_tcp(512)
        













































