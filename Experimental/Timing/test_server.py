# -*- coding: utf-8 -*-
"""
SERVER
"""

import time
import socket
import timing_utils
import struct
import random

UDP_IP_LOCAL = ''
UDP_PORT_LOCAL = 2049
UDP_PORT_REMOTE = 2050
#UDP_IP_REMOTE = '192.168.2.10'
UDP_IP_REMOTE = '127.0.0.1'

PKT_FORMAT = 'Q'*5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
sock.bind((UDP_IP_LOCAL,UDP_PORT_LOCAL))
sock.settimeout(1.000) # 10 millisecond timeout ... might be low?

# Init clock
t0 = time.clock()

time.sleep(0.001)

offsets = []
offsets_f = []

for i in range(100):
    time.sleep(.1)
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
        t4 = timing_utils.s2us(t4)
        offsets += [t1-t2]
        offsets_f += [timing_utils.get_offset_us(t1,t2,t3,t4)]
    else:
        print("Received INVALID id")
        break


    






















