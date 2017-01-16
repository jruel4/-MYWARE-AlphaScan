# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 17:31:55 2016

@author: marzipan
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from sklearn.decomposition import FastICA, PCA
from sklearn.preprocessing import normalize, scale

class MAR:    
    
    def __init__(self):
        
        '''
        Class Constants
        '''
        
        

        self.FRAME_KEYS = ["redAvg",
                           "greenAvg",
                           "blueAvg",
                           "ax",
                           "ay",
                           "az"]      
        
        self.SAMPLES_PER_FRAME = 120
        self.VARIABLES_PER_FRAME = len(self.FRAME_KEYS)     
        
        self.NUM_BUFFERS = 2
        
        self.mBuffer = [np.ones((self.SAMPLES_PER_FRAME,self.VARIABLES_PER_FRAME)) for i in range(self.NUM_BUFFERS)]
        
        self.mIntraBufIdx = [0 for i in range(self.NUM_BUFFERS)]
        
        self.mInterBufIdx = 0

        self.mDenoisedArray = np.ones((self.SAMPLES_PER_FRAME,self.VARIABLES_PER_FRAME))
    
    def step(self, frame):
        
        '''
        input: json object data frame
        output: filtered value
        '''
        pass
    
    def loadFrame(self, frame):
        for k in self.FRAME_KEYS:

            new_val = float(frame[k])            
            col_idx = self.FRAME_KEYS.index(k)
            
            self.mBuffer[self.mInterBufIdx][self.mIntraBufIdx[self.mInterBufIdx], col_idx] = new_val
            
        # Check current buffers index            
        if self.mIntraBufIdx[self.mInterBufIdx] == (self.SAMPLES_PER_FRAME - 1):
            # Switch buffers
            self.mDenoisedArray = self.denoiseCurrentBuffer()
            self.mIntraBufIdx[self.mInterBufIdx] = 0
            self.mInterBufIdx = 1 if (self.mInterBufIdx == 0) else 0
        else:
            # Increment index
            self.mIntraBufIdx[self.mInterBufIdx] += 1          
        
    def getSignal(self, key):
        return self.mBuffer[self.mInterBufIdx][:,self.FRAME_KEYS.index(key)]
        
    def getDenoisedSignal(self, key):
        return self.mDenoisedArray[:,self.FRAME_KEYS.index(key)]
    
    def denoiseCurrentBuffer(self):

        data = self.mBuffer[self.mInterBufIdx]
        
        X = scale(data)

        # Frequency Filter
        fft = np.fft.fft(X, axis=0)
        
        for j in range(fft.shape[1]):
            for i in range(int(fft.shape[0]/2)):
                if i < 4 or i > 30:
                    fft[i,j] = 0
                    fft[-(i+1),j] = 0
        
        
        # recover filtered time series
        filtX = np.fft.ifft(fft,axis=0)
        
        #return self.performICA(filtX)
        return self.performPCA(filtX)
    
    def performPCA(self, X):
        pca = PCA(n_components=X.shape[1], whiten=True)
        H = pca.fit_transform(X) 
        return H
        
    def performICA(self, X):
        
        # Compute ICA
        ica = FastICA(n_components=X.shape[1], whiten=True)
        S_ = ica.fit_transform(X) 
        return S_
        

    def endOfBuffer(self):
        return self.mIntraBufIdx[self.mInterBufIdx] == (self.SAMPLES_PER_FRAME - 1)