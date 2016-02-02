# -*- coding: utf-8 -*-
"""
Created on Mon Feb 01 18:54:23 2016

@author: marzipan
"""

import requests
import re
import subprocess # NOTE: we use Windows-specific command 'netsh' commands

#r = requests.get("http://192.168.4.1/fuck_you")

# Requirements
#   1) Connect to wireless Acess Point AlphaScanAP
#       TODO lookup netsh connection abilities - automate connection... 
#   2) Software should detect whether or not host is connected to AlphaScanAP
interfaces = subprocess.check_output(["netsh","wlan","show","interfaces"])
networks = subprocess.check_output(["netsh","wlan","show","networks"])
# TODO parse above results into usable fields
#   Information to extract:
#       - Is AlphaScanAP available? (Interfaces)
#       - Is AlphaScanAP connected? (Networks)
ApIsAvailable = ('AlphaScanAP' in networks)

def ApConnectionStatus(i):
    #TODO expand for multiple interfaces
    # Split into separate lines
    i = i.replace('\r','')
    i = i.split('\n')
    n = list()
    for e in i:
        if (len(e) > 1) and ':' in e:
            n += [(e.split(':'))]
    # Check if SSID == AlphaScanAP and State = 'connected'
    connected = False
    associated = False
    for e in n:
        if 'SSID' in e[0]:
            if 'AlphaScanAP' in e[1]:
                associated = True
        if 'State' in e[0]:
            if 'connected' in e[1]:
                connected = True
    if associated and connected:
        return True
    else:
        return False

ApConnected = ApConnectionStatus(interfaces)

# If Ap is Available but not Connected, attempt to connect
def connectToAp():
    if ApIsAvailable and not ApConnected:
        r = subprocess.check_output(["netsh","wlan","connect","name=AlphaScanAP"])
        if 'successfully' in r:
            return True
        else:
            return False
 
#   3) If not: request to do so, if so: attempt to communicate is AlphaScan
    
    
#   4) Data to exchange with alpha scan:
#       - network SSID
#       - network passkey
#       - host IP
#       - Optional: TCP port and UDP port
#   5) Note: if time consider alive/heartbeat protocol

