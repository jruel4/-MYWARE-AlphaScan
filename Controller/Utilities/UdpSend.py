# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 12:12:43 2016

@author: marzipan
"""

import socket

UDP_IP = "192.168.1.17"
UDP_PORT = 2390
num = 10
MESSAGE = chr(num)
num_iter = num * 100


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
sock.bind(('',UDP_PORT))
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

#socket.setdefaulttimeout(0)
#sock.setblocking(False)
sock.settimeout(0)

data = ''
inbuf = list()
errors = 0

while len(inbuf) < (num_iter * 0.99):
    try:
        data = sock.recv(128)
        inbuf += [ord(data[23:])]
        errors = 0
    except:
        errors += 1
        #if errors % 10000 == 0: print(errors)
        if errors > (num_iter*200): # make this relative to time 
            break
        

print("finished: "+str(len(inbuf)/float(num_iter)))



#while 'END' not in data:
#for i in range(num_iter):
#while True:
#==============================================================================
# for i in range(10):
#     try:
#         data, addr = sock.recvfrom(64)
#     except socket.error, e:
#         #print(e)
#         pass
#     except socket.timeout, e:
#         #print(e)
#         pass
#     else:
#         inbuf += [data]
#         #print(data)
#==============================================================================

#print("Finished! ",len(inbuf))

def d():
    inbuf = list()
    errors = 0
    while True:
        try:
            data,addr = sock.recvfrom(128)
            inbuf += [data]
        except socket.error:
            errors += 1
            if errors > 0: break
    
    print("finished: "+str(len(inbuf))+" / "+str(num_iter))












