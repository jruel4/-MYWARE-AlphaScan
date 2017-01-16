# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 19:29:09 2016

@author: marzipan
"""

import numpy as np
from scipy.optimize import minimize
from cardio_noise_removal.delta_freq import F,iF,nplot,freq_filter
import matplotlib.pyplot as plt

class MatchSignal:
    
    ''' Match signal assuming there is no noise '''
    
    def __init__(self, signalToMatch, NUM_COMPONENTS=3):
        
        self.Sx = signalToMatch
        self.normalizeSx()
        self.FRAME_LEN = len(self.Sx)
        
        # Constants
        self.NUM_COMPONENTS = NUM_COMPONENTS
        
        # Tunable parameters
        self.freqs = list()
        self.phis = list()
        self.mags = list()
        self.x_labels = list()
            
        self.x_labels += ['freq','mag','phi']
                         
        self.guess = [2.1,.6,0]
        
        # Target function
        self.fun_phase = lambda x: np.linalg.norm(np.angle(F(self.Sx)) - np.angle(F(self.synthesizeWave(x))))
        self.fun_mag = lambda x: np.linalg.norm(np.abs(F(self.Sx)) - np.abs(F(self.synthesizeWave(x))))
        self.fun_gen = lambda x: np.linalg.norm(self.Sx - self.synthesizeWave(x,phase_only=True))
        
        self.bounds = [(2,5),
                       (0.3,.7),
                       (-np.pi,np.pi)]
    
        self.cons = ()
        
    def synthesizeWave(self, x, phase_only=False):
        '''
        output: reasonable TS frame
        '''
        
        if phase_only:
            fr = self.guess[0]
            ma = self.guess[1]
            phi = x[0]
        else:
            fr = x[0]
            ma = x[1]
            phi = x[2]

        f = [fr,2*fr,3*fr,4*fr]
        m = [ma,.75*ma,.1*ma,.05*ma]
        t = [phi,2*phi,3*phi,4*phi]
    
        return np.reshape(sum([self.genSig(f[i],t[i],m[i]) for i in range(4)]),(30,1))
        
    def genSig(self,f,t,m):
        N=30
        return m*np.sin([(2*np.pi*f*n/N + t) for n in range(N)])

    def matchMag(self):
        res = minimize(self.fun_mag, self.guess, method='SLSQP', bounds=self.bounds, constraints=self.cons,
                       options={'disp': False, 'iprint': 1,
                                'eps': 1.4901161193847656e-01, 
                                'maxiter': 1000, 'ftol': 1e-06})
       
        self.res = res
        for i in range(3):
            self.guess[i] = res['x'][i]
        return res
        
    def matchPhase(self):
        res = minimize(self.fun_gen, [0], method='SLSQP', bounds=[(-np.pi,np.pi)], constraints=self.cons,
                       options={'disp': False, 'iprint': 1,
                                'eps': 1.4901161193847656e-01, 
                                'maxiter': 1000, 'ftol': 1e-06})
       
        self.res['x'][2] = res['x'][0]
        return res
        
    def show(self):
        nplot(self.Sx)
        self.synth = self.synthesizeWave(self.res['x'])
        plt.plot(self.synth)
        plt.legend(['original','synthesized'])
        for i,t in enumerate(self.x_labels):
            print(t,self.res['x'][i])
            
    def manual(self, f, phi, mag):
        x = [f,phi,mag]
        w = self.synthesizeWave(x)
        print("result", self.fun(x))
        nplot(self.Sx)
        plt.plot(w)
        plt.legend(['orig','synth'])
        
    def normalizeSx(self):
        #filter
        self.Sx = freq_filter(self.Sx,cutoff_high=14,cutoff_low=2)
        self.Sx = self.Sx / max(np.abs(self.Sx))[0]
    
    def setSx(self, frame):
        self.Sx = frame
        self.normalizeSx()
        
    def randomizeGuess(self):
        for i in range(len(self.guess)):
            rng = self.bounds[i][1] - self.bounds[i][0]
            self.guess[i] = rng * np.random.rand() + self.bounds[i][0]
            
    def calculateVx(self):
        '''
        Vx = VL + VG
        VL = (distance to closest reasonable profile (use fun_mag etc.)) +
             (Accelerometer magnitude in corresponding frame)
        VG = (Magnitudes np.std() away from high Vx mean)
        '''
        
    

#==============================================================================
# x = [3,6,
#      0,np.pi,
#      10,7.5]
# Sx = MatchSignal.synthesizeWave(None,x,NUM_COMPONENTS=2,FRAME_LEN=30)
#==============================================================================


sig = MatchSignal(frames[29])
sig.matchMag()
sig.matchPhase()
sig.show()
#==============================================================================
# for i in range(20):
#     sig.guess = [np.random.rand()*14 for i in range(4)]
#     sig.guess += [np.random.randn()*np.pi for i in range(4)]
#     sig.guess += [np.random.rand()*20 for i in range(4)]
#     res = sig.match()
#     #sig.show()
#     print(res['fun'])
#==============================================================================

#==============================================================================
# meths = [
# "Nelder-Mead" ,
# "Powell" ,
# "CG" ,
# "BFGS", 
# #"Newton-CG", 
# "L-BFGS-B" ,
# "TNC" ,
# "COBYLA", 
# "SLSQP" ,
# #"dogleg",
# #"trust-ncg"
# ]
# 
# 
# sine_2Hz = np.asarray([np.sin(2*np.pi*2*i/64) for i in range(64)])
# 
# def make_sin(x): return np.asarray([x[0]*np.sin(2*np.pi*2*i/64) for i in range(64)])
#     
# fun = lambda x : np.linalg.norm(sine_2Hz - make_sin(x))
# guess = [11]
# cons = ()
# bnds = [(0,15)]
# 
# 
# res = minimize(fun,guess, method="SLSQP", bounds=bnds, constraints=cons,
#                options={'disp': True, 'iprint': 1, 'eps': 1.4901161193847656e-01, 'maxiter': 1000, 'ftol': 1e-06})
# 
# 
# nplot(sine_2Hz)
# plt.plot(make_sin(res['x']))
# plt.legend(['1','2'])
# print(res)
#==============================================================================















