# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 20:33:58 2016

@author: marzipan
"""
import numpy as np
from scipy.interpolate import interp1d
from cardio_noise_removal.utils import get_data
from delta_freq import nplot, annotateMaxima

class UNIT:
    
    def __init__(self, amax1, amax2, window, srate):
        
        self.amax1 = amax1
        self.amax2 = amax2
        self.amin = window[amax1:amax2].argmin() + amax1
        
        bottom = window[self.amin]
        
        self.a1 = window[amax1] - bottom
        self.a2 = window[amax2] - bottom
        self.t1 = (self.amin-amax1)/srate
        self.t2 = (amax2-self.amin)/srate
            
        self.ita = self.ITA(self.a1,self.t1,self.a2,self.t2)
        self.width = abs((amax2-amax1)/srate)
    
    def ITA(self,a1,t1,a2,t2):
        return 0.5*(a1*t2+a2*t1)
        
        

def resample(x, y):
    f = interp1d(x, y, kind='cubic')
    new_x = np.linspace(x[0],x[-1],num=len(x))
    return f(new_x)

def smooth3pt(signal):
    a = 1.0/3.0
    return np.convolve(signal,[a,a,a],mode='same')

def construct_maxima_list(signal):
    maxima = list()    
    for t in range(1,len(signal)-1):
        if (signal[t-1]<signal[t] and signal[t+1]<signal[t]):
            maxima += [t]
    return maxima
    
def construct_minima_list(signal):
    maxima = list()    
    for t in range(1,len(signal)-1):
        if (signal[t-1]>signal[t] and signal[t+1]>signal[t]):
            maxima += [t]
    return maxima

def reform(signal):
    signal = np.asarray(signal)
    signal = signal.reshape((len(signal),)) 
    return signal
    
def get_threshold(time,signal):
    # get threesecond window
    period = (time[-1]-time[0])/1000.0
    srate = abs(len(time)/period)
#==============================================================================
#     N = int(3.0*srate)
#==============================================================================
    N = 25
    max1 = 0
    max2 = 0
    idx = 0
    first = True
    MIN_INTERVAL = 0.5
    MAX_INTERVAL = 1.2
    
    # TODO must intelligently restrict window size N and max and min width according to 
    # global and local statistics, for now try manual tuning
    
    while((idx+N) < len(signal)):
        window= signal[idx:idx+N]
        # find max amplitude rising edgee
        maxima = construct_maxima_list(window)
        minima = construct_minima_list(window)
        join = sorted(minima+maxima)
        diffs = np.asarray([window[join[i+1]]-window[join[i]] for i in range(len(join)-1)])
        max2 = join[diffs.argmax()+1]
        
        #Calc unit from max1, max2
        width = abs((max2-max1)/srate) # in seconds
        argbottom = window[max1:max2].argmin()
        bottom = window[max1+argbottom]
        amp1 = window[max1]-bottom
        amp2 = window[max2]-bottom
        
        if (width > MIN_INTERVAL) and (width < MAX_INTERVAL) and (amp1 < 2*amp2) and (amp2 < 2*amp1) and (not first):
            # construct unit and return ita
            unit = UNIT(max1,max2,window, srate)
            return unit.ita
            
        else:
            # if not pass criteria then slide
            max1 = 0
            idx += max2
            first = False
    print("FAILED")
    return -1
    
class ItaPeakDetector:
    
    def __init__(self):
        self.MIN_INTERVAL = 0.3 # seconds
        self.MAX_INTERVAL= 1.5 # seconds
        
        data = get_data()
        self.signal = data[:,0]
        self.time = data[:,7]
        self.signal = reform(self.signal)
        self.time = reform(self.time)
        self.period = (self.time[-1]-self.time[0])/1000.0
        self.srate = abs(len(self.time)/self.period)
        self.smoothed = smooth3pt(resample(self.time,self.signal))
        
        self.threshold = get_threshold(self.time,self.smoothed)
            
        self.UNIT_LIST = list()
        self.count = 0
        self.alpha = 0.75
        self.beta = 0.9
        
        self.unit = None
        
        self.global_maxima = construct_maxima_list(self.smoothed)
        self.global_minima = construct_minima_list(self.smoothed)
        self.global_zeros = sorted(self.global_minima+self.global_maxima)
        self.g_max_idx = 0
        
        self.peaks = set()
        self.accepted_units = list()
        
        #TODO need do modify self.MIN/MAX_INTERVAL and also self.threshold more intelligently
        
    def detect(self):
        while(True): #TODO add termination criteria
            if self.unit != None and self.unit.width >= self.MIN_INTERVAL:                
                if self.unit.width > self.MAX_INTERVAL:
                    self.UNIT_LIST = self.UNIT_LIST[1:]
                    self.unit = self.merge_unit()
                    continue
                elif (self.unit.ita >= ((2.0/5.0)*self.threshold) and (self.unit.ita <= 2*self.threshold)):
                    self.UNIT_LIST = list()
                    self.count += 1
                    self.threshold = self.alpha*self.threshold+(1-self.alpha)*self.unit.ita
                    self.peaks.add(self.unit.amax1)
                    self.peaks.add(self.unit.amax2)
                    self.accepted_units += [self.unit]
                else:
                    self.threshold = self.beta*self.threshold+(1-self.beta)*self.unit.ita
            
            self.unit = self.get_unit()
            if not self.unit:
                print("Finished")
                return
            self.unit = self.merge_unit()
    
    
    
    
    def get_unit(self):
        '''
        detect falling edge and subsequent rising edge to construct a unit, add to unit list
        Really just get next maxima from pre-generated list and construct unit
        '''
        # get next maxima
        m1 = self.global_maxima[self.g_max_idx]
        self.g_max_idx += 1
        if self.g_max_idx >= len(self.global_maxima):
            return False
        m2 = self.global_maxima[self.g_max_idx]
        
        #construct unit    
        u = UNIT(m1,m2,self.smoothed, self.srate)
        self.UNIT_LIST += [u]
        return u
        
        
    
    def merge_unit(self):
        '''
        use p1 of first unit and p2 of last, and lowest of all to construct new unit
        '''
        u1 = self.UNIT_LIST[0]
        u2 = self.UNIT_LIST[-1]
        return UNIT(u1.amax1,u2.amax2,self.smoothed, self.srate)
        
    def show(self):
        nplot(self.smoothed)
        annotateMaxima(self.peaks,self.smoothed)
        


d = ItaPeakDetector()
d.detect()
d.show()

    
    
    
    
    
    