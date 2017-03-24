# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 15:17:49 2017

@author: marzipan
"""

import numpy as np
from threading import Thread 
from vispy import plot as vp
from pylsl import StreamInlet, resolve_stream
import time

streams = list()
def select_stream():
    streams = resolve_stream('type', 'EEG')
    for i,s in enumerate(streams):
        print(i,s.name())
    stream_id = input("Input desired stream id: ")
    inlet = StreamInlet(streams[int(stream_id)])    
    return inlet
    
inlet = select_stream()
#sample, timestamp = inlet.pull_sample()

fs=250
fig = vp.Fig(show=False)

spec = list()
for r in range(4):
    for c in range(2):        
        spec += [fig[r,c].spectrogram(np.zeros((256*200)), fs=fs, clim=(0, 8))]

new_data = spec[0]._data
new_data = np.zeros_like(new_data)

new_datas = [np.zeros_like(new_data) for i in range(8)]

def update():
    global inlet, new_data, spec, sample

    begin = time.time()    
    jdx = 0
    
    while True:

        jdx += 1
        if jdx % 60 == 0:
            print("fps: ",jdx/(time.time()-begin))
        
        sample, timestamp = inlet.pull_sample()
        sample = np.asarray(sample)
        sample = sample.reshape((129,8))
        for idx in range(8):
            ch_samples = sample[:,idx]
            k = 1
            new_datas[idx][:, :-k] = new_datas[idx][:, k:]
            new_datas[idx][:, -k:] = ch_samples[:,None]
            spec[idx].set_data(new_datas[idx])

        fig.update()

if __name__ == '__main__':
    fig.show(run=True)
    thread = Thread(target=update)
    thread.start()
    
    
    