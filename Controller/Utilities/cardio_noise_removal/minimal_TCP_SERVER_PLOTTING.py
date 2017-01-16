
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 12:52:36 2016

@author: marzipan
"""

filt = [
  0.0001389353612909,0.0001302664715596,0.0001866450611829,0.0002546646511985,
  0.0003343440783187,0.0004249381298279, 0.000524999352213,0.0006322966302564,
  0.0007437596991247, 0.000855044923045,0.0009614082304368, 0.001056712805112,
   0.001134333874601, 0.001186767605592, 0.001206019140551, 0.001183873881178,
   0.001112039072207,0.0009825411546261,0.0007880768615829,0.0005222801174633,
  0.0001802822431626,-0.0002410429659627,-0.000742622039604,-0.001322835133346,
  -0.001977291615553,-0.002698473096725,-0.003475651094107,-0.004294736837549,
  -0.005138306321372,-0.005985743066104,-0.006813460269658,-0.007595248675386,
  -0.008302778176771,-0.008906091214489,-0.009374360835302,-0.009676563131749,
  -0.009782373197899,-0.009662999220458,-0.009292099608954,-0.008646652923542,
  -0.007707839128281,-0.006461797257043,-0.004900400714486,-0.003021795105599,
  -0.0008309315165195, 0.001660183060538, 0.004432315994968, 0.007459095527535,
    0.01070723885528,  0.01413701818327,  0.01770286199544,  0.02135420197662,
    0.02503640221269,  0.02869191127555,  0.03226144856545,   0.0356853351533,
    0.03890482375982,  0.04186347095261,  0.04450845454926,  0.04679184526703,
    0.04867174940774,  0.05011334283959,  0.05108971275706,  0.05158253771499,
    0.05158253771499,  0.05108971275706,  0.05011334283959,  0.04867174940774,
    0.04679184526703,  0.04450845454926,  0.04186347095261,  0.03890482375982,
     0.0356853351533,  0.03226144856545,  0.02869191127555,  0.02503640221269,
    0.02135420197662,  0.01770286199544,  0.01413701818327,  0.01070723885528,
   0.007459095527535, 0.004432315994968, 0.001660183060538,-0.0008309315165195,
  -0.003021795105599,-0.004900400714486,-0.006461797257043,-0.007707839128281,
  -0.008646652923542,-0.009292099608954,-0.009662999220458,-0.009782373197899,
  -0.009676563131749,-0.009374360835302,-0.008906091214489,-0.008302778176771,
  -0.007595248675386,-0.006813460269658,-0.005985743066104,-0.005138306321372,
  -0.004294736837549,-0.003475651094107,-0.002698473096725,-0.001977291615553,
  -0.001322835133346,-0.000742622039604,-0.0002410429659627,0.0001802822431626,
  0.0005222801174633,0.0007880768615829,0.0009825411546261, 0.001112039072207,
   0.001183873881178, 0.001206019140551, 0.001186767605592, 0.001134333874601,
   0.001056712805112,0.0009614082304368, 0.000855044923045,0.0007437596991247,
  0.0006322966302564, 0.000524999352213,0.0004249381298279,0.0003343440783187,
  0.0002546646511985,0.0001866450611829,0.0001302664715596,0.0001389353612909
]

import socket
from collections import deque
import pyqtgraph as pg
import select
import numpy as np
from scipy.signal import filtfilt

def twos_comp(val, bits=24):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val 
    
'''Data Params '''
window_len = 250
NUM_CHANNELS = 8
buffers = [deque([0 for i in range(window_len)], window_len) for i in range(NUM_CHANNELS)]
freqs = np.linspace(0,125,num=1250)

'''Networking Params'''
TCP_IP = ''
TCP_PORT = 8200
BUFFER_SIZE = 2048  

'''Init Socket'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for client to connect...")
conn, addr = s.accept()

conn.setblocking(0)

print("connected to:",addr)

s.setblocking(0) #non blocking

'''Setup Plotting Objects'''
NUM_ROWS = 2
#Create widgets
plt = list()
for i in range(NUM_CHANNELS):
    plt_title = "Channel "+str(i)
    plt += [pg.plot(buffers[i], title=plt_title)]
    pg.QtGui.QApplication.processEvents()

print("created plots")

data = str()

idx = 0
rd_count = 0

while True:
    
    idx += 1    
    
    try:
        
        ready = select.select([conn], [], [], 0) # wait until s is ready
        if ready[0]:
            data += conn.recv(BUFFER_SIZE)
            rd_count += 1
        
        # look for start byte
        start_byte = 0x7f
        msg = None
        if len(data) < 27:
            print("data too small")
            continue
        for i in range(len(data)):
            if (ord(data[i]) == start_byte) and (ord(data[i+1]) == start_byte)\
            and (ord(data[i+2]) == start_byte) and (ord(data[i+3]) == start_byte):
                msg = data[i+4:i+28]
                data = data[i+29:]
                break
        if msg == None or len(msg) != 24:
            print("skipped")
            continue
            
        new_vals = list()
        deviceData = list()

        for j in xrange(8):
            deviceData += [msg[j*3:j*3+3]]
            val = 0
            for s,n in list(enumerate(reversed(deviceData[j]))):
                val ^= ord(n) << (s*8)
            val = twos_comp(val)
            new_vals += [val]
                
        if len(new_vals) != 8:
            print("Found incorrect number of values: ",len(new_vals))
            continue
        else:
            #Add new val to appropriate buffer deque
            for i in range(NUM_CHANNELS):
                buffers[i].append(int(new_vals[i]))
                #print(i,new_vals[i])
#==============================================================================
#                 if new_vals[i] != 0:
#                     #print("found non zero",new_vals[i],bin(new_vals[i]))
#                     break
#==============================================================================
        
        if idx%20 == 0:
            for i in range(NUM_CHANNELS):
                plt[i].plot(buffers[i],clear=True)
#==============================================================================
#                 if i ==1:
# 
#                     filtered = filtfilt(filt, [1], buffers[i])
#                     plt[i-1].plot(filtered, clear=True)
#                     plt[i].plot(buffers[i], clear=True)
#                     plt[i+1].plot(freqs, np.abs(np.fft.fft(buffers[i]))[0:1250], clear=True)
#                     plt[7].plot(buffers[7],clear=True)
#                     break
#==============================================================================
            
        #print("len data:",len(data))
            
    except KeyboardInterrupt:
        break
    except socket.timeout:
        print("timeout")
    
    pg.QtGui.QApplication.processEvents()

pg.QtGui.QApplication.processEvents()

conn.close()

s.close()
print("connection closed")

