# -*- coding: utf-8 -*-
"""
SERVER
"""

import time
import socket
import timing_utils 
import struct
import random
import numpy as np
# timeit.default_timer() == best clock on given system, time.clock() for windows

# t1 = Tx1
# t2 = Rx1
# t3 = Tx2
# t4 = Rx2

# (t2-t1) == +(1 way travel time + clock offset)
# (t3-t4) == -(1 way travel time - clock offset)
# Clock Offset = ((t2-t1)+(t3-t4))/2

# 12 hour timer == 12*60*60*1E6 == 43200000000.0 microseconds

UDP_IP_LOCAL = ''
UDP_PORT_LOCAL = 2049
UDP_PORT_REMOTE = 2050
UDP_IP_REMOTE = '127.0.0.1'

PKT_FORMAT = 'Q'*5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
sock.bind((UDP_IP_LOCAL,UDP_PORT_LOCAL))
sock.settimeout(0.010) # 10 millisecond timeout ... might be low?

# Init clock
t0 = time.clock()

NUM_TRIALS = 1000
OFFSETS = []

for i in range(NUM_TRIALS):
    time.sleep(0.001)

    # Generate packet id
    pid = random.randint(0,2**64-1)
    
    # Generate t1, pkt1, and immediatly send
    t1 = timing_utils.s2us(time.clock())
    pkt1 = struct.pack(PKT_FORMAT, pid, t1, 0, 0, 0)
    sock.sendto(pkt1, (UDP_IP_REMOTE,UDP_PORT_REMOTE))
    
    # Block wait for rx with reasonable timeout (timeout ~ max expected RTT)
    rx_data = sock.recv(256)
    
    # Upon receipt immediatly generate t4
    t4 = time.clock()
    
    # Check if packet is correct
    rx_pid,t1,t2,t3,_ = struct.unpack(PKT_FORMAT, rx_data)
    
    if rx_pid == pid:
        offset = timing_utils.get_offset_us(t1,t2,t3,t4)
        OFFSETS += [offset]
    else:
        print("Received INVALID id")
        break

stats_labels = ['mean', 'std', 'max', 'min']
stats_vals = []
# Calculate offset statistics
OFFSETS = np.asarray(OFFSETS)
stats_vals += [np.mean(OFFSETS)]
OFFSETs_Z = OFFSETS - stats_vals[0]
stats_vals += [np.std(OFFSETs_Z)]
stats_vals += [np.max(OFFSETs_Z)]
stats_vals += [np.min(OFFSETs_Z)]

for i in range(len(stats_labels)):
    print(stats_labels[i],stats_vals[i])





























