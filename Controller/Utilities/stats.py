# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 00:22:38 2017

@author: marzipan
"""
import numpy as np
def rms(d): return np.sqrt(np.mean((d-np.mean(d))**2))
    
def get_imp(d):
    b2v = 5.0/(2**24)
    V = (max(d) - min(d))*b2v
    I = 24E-6
    return V/I
    
#==============================================================================
# ivt = list()
# win_len = 250
# for i in range(len(data)-win_len):
#     frame = data[i:i+win_len]
#     ivt += [get_imp(frame)]
#==============================================================================
