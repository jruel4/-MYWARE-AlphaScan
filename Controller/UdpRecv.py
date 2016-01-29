# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 12:19:35 2016

@author: marzipan
"""

import socket

UDP_IP = ""
UDP_PORT = 2390

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
sock.settimeout(0.05)


data, addr = sock.recvfrom(1024)
print("received message: ", data, addr)
    
    
    
    
    
    
    
    
    
    