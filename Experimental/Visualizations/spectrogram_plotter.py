# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 06:45:35 2017

@author: marzipan
"""

# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 1
"""
A spectrogram and waveform plot of 1D data.
"""

import numpy as np
from threading import Thread
from vispy import plot as vp
from pylsl import StreamInlet, resolve_stream

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
fig = vp.Fig(size=(800, 400), show=False)
spec = fig[0,0].spectrogram(np.zeros((256*600)), fs=fs, clim=(0, 8))

new_data = spec._data
new_data = np.zeros_like(new_data)

def update():
    global inlet, new_data, spec, sample
    while True:
        sample, timestamp = inlet.pull_sample()
        sample = np.asarray(sample)
        sample = sample.reshape((129,8))
        ch1_samples = sample[:,5]
        k = 1
        new_data[:, :-k] = new_data[:, k:]
        new_data[:, -k:] = ch1_samples[:,None]
        spec.set_data(new_data)
        spec.update()

if __name__ == '__main__':
    fig.show(run=True)
    thread = Thread(target=update)
    thread.start()
