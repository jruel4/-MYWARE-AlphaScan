# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 14:32:07 2017

@author: marzipan
"""

import socket
import time

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 50007))

  
s.settimeout(2)
s.listen(10)        
time.sleep(0.5)
conn,addr = s.accept()

conn.send("ssid_key::MartianWearablesLLC* ,\
                          pass_key::phobicbird712* ,\
                          ip_key::192.168.2.5* ,\
                          port_key::50007* ,")
                          
                          
                          
