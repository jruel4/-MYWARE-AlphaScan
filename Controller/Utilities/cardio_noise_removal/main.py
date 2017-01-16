# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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
#==============================================================================
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
# ax1.plot(np.abs(fft))
#==============================================================================


# recover filtered time series
#filtX = np.fft.ifft(fft,axis=0)
    
    
'''Normalize Data'''

# Zero mean

# Unit variance
    


data = get_data()

X = scale(data)

# Frequency Filter
fft = np.fft.fft(X, axis=0)

for j in range(fft.shape[1]):
    for i in range(int(fft.shape[0]/2)):
        if i < 4 or i > 30:
            fft[i,j] = 0
            fft[-(i+1),j] = 0

#==============================================================================
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
# ax1.plot(np.abs(fft))
#==============================================================================


# recover filtered time series
filtX = np.fft.ifft(fft,axis=0)
#==============================================================================
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
# ax1.plot(filtX)
#==============================================================================

# Compute ICA
ica = FastICA(n_components=filtX.shape[1], whiten=False)
S_ = ica.fit_transform(filtX)  # Reconstruct signals
A_ = ica.mixing_  # Get estimated mixing matrix

#==============================================================================
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
# ax1.plot(S_)
#==============================================================================

# We can `prove` that the ICA model applies by reverting the unmixing.
#==============================================================================
# assert np.allclose(X, np.dot(S_, A_.T) + ica.mean_)
#==============================================================================

# For comparison, compute PCA
pca = PCA(n_components=filtX.shape[1], whiten=True)
H = pca.fit_transform(filtX)  # Reconstruct signals based on orthogonal components

#==============================================================================
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
# ax1.plot(H)
#==============================================================================
#==============================================================================
# 
# f1 = plt.figure()
# ax1 = f1.add_subplot(111)
#==============================================================================


#==============================================================================
# markers_on = list()
# ax1.plot(H, '-gD', markevery=markers_on)
#==============================================================================


aft = S_[:,0]
bef = data[:,0]

comp = scale(np.vstack((bef,aft)).T)

bef = comp[:,0]
aft = comp[:,1]

f1 = plt.figure()
ax1 = f1.add_subplot(111)

markers_bef = signal.argrelmax(bef)[0]
markers_aft = signal.argrelmax(aft)[0]

ax1.plot(bef,'-D', markevery=markers_bef)
ax1.plot(aft,'-D', markevery=markers_aft)

plt.legend(['before','after'])

#plt.legend(['red', 'green', 'blue', 'luma', 'ax', 'ay', 'az'])


