# -*- coding: utf-8 -*-
"""
CLIENT
"""
import time
import socket
import timing_utils 
import struct

UDP_IP_LOCAL = ''
UDP_PORT_LOCAL = 2050

PKT_FORMAT = 'Q'*5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,8192)
sock.bind((UDP_IP_LOCAL,UDP_PORT_LOCAL))

# Init clock
t0 = time.clock()

# Block recv UDP sock
try:
    while True:
        rx_data,REMOTE_ADDR = sock.recvfrom(256)
        
        # Generate rx timestamp t2
        t2 = time.clock()
        
        # Unpack 
        rx_pid,t1,t2,_,_ = struct.unpack(PKT_FORMAT, rx_data)
        
        # Generate pkt2
        t2 = timing_utils.s2us(t2)
        t3 = timing_utils.s2us(time.clock())
        pkt2 = struct.pack(PKT_FORMAT, rx_pid, t1, t2, t3, 0)
        
        # Send plt2
        sock.sendto(pkt2, REMOTE_ADDR)
        
        #print("Processed request",rx_pid)
except KeyboardInterrupt:
    print("Exiting...")
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    