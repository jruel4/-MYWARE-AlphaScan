# -*- coding: utf-8 -*-
"""
Created on Mon Feb 01 18:54:23 2016

@author: marzipan
"""

import requests
import subprocess # NOTE: we use Windows-specific command 'netsh' commands

class ApConnection:
    
    def __init__(self):
        ''' ApConnection Class Initialization routine'''
        self.interfaces = str()
        self.networks = str()
        self.ApIsAvailable = False
        self.connected = False
        self.associated = False
    
    def read_network_card(self):
        ''' Populate available interfaces and networks, then check to see if 
            AlphaScan access point is available and/or connected.'''
        self.interfaces = subprocess.check_output(["netsh","wlan","show","interfaces"])
        self.networks = subprocess.check_output(["netsh","wlan","show","networks"])
        self.ApIsAvailable = ('AlphaScanAP' in self.networks)
        self.ApConnected = self.ap_connection_status(self.interfaces)

    def ap_connection_status(self,i):
        ''' Parse the interfaces return string to check whether there is a current
            connection to the AP.'''
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

    def connect_to_ap(self):
        ''' If the AP is available but not connected, connect to it. '''
        # TODO trouble shoot if profile not currently available - researsh says not possible...
        if self.ApIsAvailable and not self.ApConnected:
            r = subprocess.check_output(["netsh","wlan","connect","name=AlphaScanAP"])
            if 'successfully' in r:
                return True
            else:
                return False
 
#   3) If not: request to do so, if so: attempt to communicate is AlphaScan
    def test_ap_connection(self):
        ''' Query to see if connection to AlphaScanAP is valid. '''
        r = requests.get("http://192.168.4.1/alive?")
        if 'IAMALPHASCAN' in r.text:
            return True
        else:
            return False
            
    def query_ap(self,query_text):
        ''' Send arbitrary query text to ap '''
        #TODO make these requests non blocking or short timeout
        r = requests.get("http://192.168.4.1/"+query_text)
        return r.text

# TODO remove this test driver

conn = ApConnection()
conn.read_network_card()
print("connected:        "+str(conn.ApConnected))
print("available:        "+str(conn.ApIsAvailable))
#print("connection valid: "+str(conn.test_ap_connection()))
#==============================================================================
# conn.query_ap('host_ip_192.168.1.8_endhost_ip')
# conn.query_ap('pass_BSJKMVQ6LF2XH6BJ_endpass')
# conn.query_ap('ssid_PHSL2_endssid')
# conn.query_ap('GO')
#==============================================================================

#   4) Data to exchange with alpha scan:
#       - network SSID
#       - network passkey
#       - host IP
#       - Optional: TCP port and UDP port
#   5) Note: if time consider alive/heartbeat protocol

