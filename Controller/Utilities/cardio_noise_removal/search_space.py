# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 18:30:02 2016

@author: marzipan
"""

import numpy as np
from scipy.signal import square
from cardio_noise_removal.delta_freq import addPhase

''' How large is the 'reasonable solution space' for our original signal? '''

'''
Assuming parameters:
-f bpm for [40,120] : M==80
-theta for [-pi,pi] by pi/30 : M==60xN
-mag for [0,1] by 0.01 : M==100xN

'''

def magSpace(N):
    return 80*60*100*(N**2)



def genSig(f,t,m):
    N=30
    return m*np.sin([(2*np.pi*f*n/N + t) for n in range(N)])
    
def genSq(f,t,m):
    N=300
    return m*square([2*np.pi*f*n/N + t for n in range(N)], duty=.7)  
    
def genquad(fr,ma,phi):
    f = [fr,2*fr,3*fr,4*fr]
    m = [ma,.75*ma,.1*ma,.05*ma]
    t = [phi,2*phi,3*phi,4*phi]
    
    return np.reshape(sum([genSig(f[i],t[i],m[i]) for i in range(4)]),(30,1))
    
    
def match_rough(frame):
    f = np.linspace(2.5,5,num=40)
    theta = np.linspace(-16*np.pi/16,16*np.pi/16,num=60)
    #mag = np.linspace(.5,.6,num=20)
    norm = 1000
    count = 0
    for fr in f:
        for t in theta:
            #diff = np.linalg.norm(np.abs(F(fsig))- np.abs(F(genSig(fr,t,m)+genSig(2*fr,t+3*np.pi/8,0.7*m))))
            diff = np.linalg.norm(frame - genquad(fr,.5,t) )          
            if diff < norm:
                norm = diff
                fm = fr
                tm = t
                mm = .5
                
            count += 1
            if count % 10000 ==0:
                print(count)
            
    print(diff)
    print(fm,tm)
    return genquad(fm,mm,tm)
    
    #nplot(genSig(fm,tm,mm) + genSig(2*fm,tm-3*np.pi/8,mm*0.75))
#==============================================================================
#     print("diff",diff)
#     #nplot(genSig(fm,tm,mm)+genSig(2*fr,t+2*np.pi/8,0.7*m))
#     nplot(genquad(3,mm,3*np.pi/16))
#     plt.plot(fsig)
#     plt.legend(['synth','original'])
#     
#==============================================================================

#TODO predict subsequent phase based on previous frequency and phase

def predict_phase(f,p):
    # p is the phase at the beginning of the previous frame
    # how many cycle fit in a frame? exactly f cycles...
    advance = f * 2 * np.pi
    return addPhase(p,advance)

















