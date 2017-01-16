# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 16:51:52 2016

@author: marzipan
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from sklearn.decomposition import FastICA, PCA
from sklearn.preprocessing import normalize, scale

def get_data():
    import json
    
    path = '/home/marzipan/Desktop/data_dumps/'
    file = 'dump_at_1473842294773.json'
    
    with open(path+file) as json_data:
        d = json.load(json_data)
        
    # load series from children
    N = len(d['children'])
    
    green = list()
    red = list()
    blue = list()
    ax = list()
    ay = list()
    az = list()
    luma = list()
    timestamp = list()
    ids = list()
    
    for child in d['children']:
        green += [child["green_avg"]]
        red += [child["red_avg"]]
        blue += [child["blue_avg"]]
        ax += [child["accel_x"]]
        ay += [child["accel_y"]]
        az += [child["accel_z"]]
        luma += [child["luma"]]
        timestamp += [child["timestamp"]]
        ids += [child["id"]]
        
    
    segment_cuttoff = 1265 # 0:1265
    
    return (np.matrix([red, green, blue, luma, ax, ay, az, timestamp])[:,0:segment_cuttoff]).T
    
def freq_filter(X, cutoff_low=20, cutoff_high=500):
    
    fft = np.fft.fft(X, axis=0)

    for j in range(fft.shape[1]):
        for i in range(int(fft.shape[0]/2)):
            if i < cutoff_low or i > cutoff_high:
                fft[i,j] = 0
                fft[-(i+1),j] = 0
    
    return np.fft.ifft(fft,axis=0)
    
def plt_spec(x):
    plt.plot(np.abs(np.fft.fft(x, axis=0)[0:int(len(x)/2)]))
    
def logcosh(x, fun_args=None):
#==============================================================================
#     alpha = fun_args.get('alpha', 1.0)  # comment it out?
#==============================================================================
    alpha = 1.0

    x *= alpha
    gx = np.tanh(x, x)  # apply the tanh inplace
    g_x = np.empty(x.shape[0])
    # XXX compute in chunks to avoid extra allocation
    for i, gx_i in enumerate(gx):  # please don't vectorize.
        g_x[i] = (alpha * (1 - gx_i ** 2)).mean()
    return gx, g_x