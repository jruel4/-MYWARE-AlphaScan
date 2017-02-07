# -*- coding: utf-8 -*-
"""
Created on Tue Feb 07 00:54:53 2017

@author: marzipan
"""

import matplotlib.pyplot as plt
import numpy as np
import socket
import time

UDP_IP = "192.168.1.227"
UDP_PORT = 50007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
sock.bind(('',UDP_PORT))

def msg(c):
    return chr(c)+'_'.encode('utf-8')+chr(0x00)     
def get_newest_ctr(sock):
        valid = 0
        nctr = -1
        sndr_rc = -1
        while 1:
            try:
                data = sock.recv(1400)
                nctr = ord(data[0])
                sndr_rc = ord(data[2])
                valid = len(data)
            except socket.timeout:
                break
            except socket.error as e:
            # A non-blocking socket operation could not be completed immediately
                if e.errno == 10035: 
                    break
                else:
                    raise e
        return nctr,valid,sndr_rc

l_l_delays = list()
l_skip = list()
l_miss = list()
l_totrx = list()
l_kBps = list()
l_tp = list()
l_max_d = list()
l_min_d = list()
l_av_d = list()
l_sd_d = list()

sleeps = np.linspace(0.015,0.040,num=8)

for i in range(2):
    for sleep in sleeps:
    
        # Stat vars
        do_print = False
        pd = 10.0 # print delta
        pl = time.time() # print last
        dl = list() # delay list
        rp = time.time() # rx previous
        rc = 0 # rx current
        
        # Core vars
        sock.settimeout(0)
        totrx = 0
        skip = -1
        miss = 0
        te = 60*2
        t0 = time.time()
        ctr = 0x00
        while (time.time()-t0)<te:
            sock.sendto(msg(ctr), (UDP_IP, UDP_PORT))    
            time.sleep(sleep) 
            nctr,valid,rc = get_newest_ctr(sock)   
            if not valid: miss+=1;
            elif nctr != (ctr+1)%256: ctr=nctr;skip+=1
            else: ctr=nctr;totrx+=valid;rc=time.time();dl+=[rc-rp];rp=rc
            
            # Stats code
            if ((time.time()-pl)>pd) and do_print:
                pl = time.time()
                print("sleep: ",sleep)
                print("skip:  ",skip)
                print("miss:  ",miss)
                print("totrx: ",totrx)
                print("kBps:  ",totrx/1000.0/te)
                print("%tp:   ",(totrx/1400.0)/(te/sleep)*100)
                print("-------------------------")
        
        dl = dl[1:] # discard first value
        if do_print:        
            print("sleep:     ",sleep)
            print("skip:      ",skip)
            print("miss:      ",miss)
            print("totrx:     ",totrx)
            print("kBps:      ",totrx/1000.0/te)
            print("%tp:       ",(totrx/1400.0)/(te/sleep)*100)
            print("max delay: ",max(dl))
            print("min delay: ",min(dl))
            print("av. delay: ",np.mean(dl))
            print("sd. delay: ",np.std(dl))
            print("-------------------------")
        l_l_delays += [dl]
        l_skip += [skip]
        l_miss += [miss]
        l_totrx += [totrx]
        l_kBps += [totrx/1000.0/te]
        l_tp += [(totrx/1400.0)/(te/sleep)*100]
        l_max_d += [max(dl)]
        l_min_d += [min(dl)]
        l_av_d += [np.mean(dl)]
        l_sd_d += [np.std(dl)]
        #1400 generated every 46 milliseconds

print("kBps")
plt.plot(sleeps,l_kBps)
plt.show()
print("Max Delay")
plt.plot(sleeps,l_max_d)
plt.show()
print("Min Delay")
plt.plot(sleeps,l_min_d)
plt.show()
print("Average Delay")
plt.plot(sleeps,l_av_d)
plt.show()
print("Standard Deviation Delay")
plt.plot(sleeps,l_sd_d)
plt.show()
print("% Throughput")
plt.plot(sleeps,l_tp)
plt.show()




















