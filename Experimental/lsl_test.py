# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 11:45:35 2017

@author: marzipan
"""

from pylsl import StreamInfo, StreamOutlet
import random

info = StreamInfo('AlphaScan', 'EEG', 8, 100, 'float32', 'myuid34234')
outlet = StreamOutlet(info)

while (True):
    mysample = [random.random(), random.random(), random.random(),
            random.random(), random.random(), random.random(),
            random.random(), random.random()]
    outlet.push_sample(mysample)
            
        