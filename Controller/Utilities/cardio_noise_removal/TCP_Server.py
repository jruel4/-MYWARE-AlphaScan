# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 12:52:36 2016

@author: marzipan
"""

import socket
from collections import deque
import json
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from MotionArtifactReduction import MAR

'''Data Params '''
window_len = 60
redvalues = deque([0 for i in range(window_len)], window_len)
timestamps = deque([i for i in range(window_len)], window_len)

'''Networking Params'''
TCP_IP = ''
TCP_PORT = 51718
BUFFER_SIZE = 1024  

'''Init Socket'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for client to connect...")
conn, addr = s.accept()
print("connected to:",addr)

import select

s.setblocking(0)

ready = select.select([s], [], [], 1)

w = QtGui.QWidget()
#Create widgets
plt = list()
mar = MAR()
num_plots = mar.VARIABLES_PER_FRAME * 2
for i in range(num_plots):
    plt += [pg.PlotWidget()]
## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
NUM_ROWS = 3
w.setLayout(layout)
for i in range(num_plots):
    layout.addWidget(plt[i],i%NUM_ROWS, i//NUM_ROWS, 1,1)  
## Display the widget as a new window
w.show() 



    
while True:
    
#==============================================================================
#     print(str(conn.recv(BUFFER_SIZE)))
#     continue
#==============================================================================
    
    try:
        data = str(conn.recv(BUFFER_SIZE))
        
        beg = data.find("xbx")
        end = data.find("xex")
    
        if beg != -1 and end != -1 and (end > beg):
            data = data[beg+3:end]
        
            frame = json.loads(data)
            
            redvalues.append(float(frame["redAvg"]))
            
            # Apply MAR Algorithm
            mar.loadFrame(frame)
            
            
            for i in range(num_plots):
                
                if i < mar.VARIABLES_PER_FRAME:
                    plt[i].plot(mar.getSignal(mar.FRAME_KEYS[i]), clear=True)
                else:
                    plt[i].plot(mar.getDenoisedSignal(mar.FRAME_KEYS[i%mar.VARIABLES_PER_FRAME]), clear=True)
                
                
                
#==============================================================================
#                 if mar.endOfBuffer():
#                     plt[1].plot(mar.denoiseCurrentBuffer(), clear=True)
#==============================================================================
                
            
            time.sleep(0)
        
            
        else: 
            print("invalid packet", data)
            
        
    except KeyboardInterrupt:
        break
    except socket.timeout:
        print("timeout")
        
    pg.QtGui.QApplication.processEvents()
        

        
for p in plt:
    p.close()
w.close()

conn.close()

s.close()
print("connection closed")


