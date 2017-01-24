# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 00:04:33 2016

@author: marzipan
"""

import socket
import select
import numpy as np
import sys
import time

'''Networking Params'''
TCP_IP = ''
TCP_PORT = 51718
BUFFER_SIZE = 256 # MM  

'''Init Socket'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for client to connect...")
conn, addr = s.accept()

conn.setblocking(0)

print("connected to:",addr)

s.setblocking(0) #non blocking

data = bytes()
time_begin = time.time()
while True:   
    try:    
        ready = select.select([conn], [], [], 0) # wait until s is ready
        if ready[0]:
            data += conn.recv(BUFFER_SIZE)

            # extract counter and send to LSL
            if (len(data) >= 256):
                
                rec = 0
                for i in range(4):
                    rec |= (data[i] << (8*i))
                
                data = data[256:]
    
                print(rec)
  
        bps = len(data)/(time.time()-time_begin)/1000.0
            
        #sys.stdout.write("Tx rate (bps): %d%%   \r" % (bps) )
        #sys.stdout.flush()
        time.sleep(0)
        
    except KeyboardInterrupt:
        break
    
conn.close()
s.close()
