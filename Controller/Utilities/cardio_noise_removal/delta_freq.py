# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 16:45:46 2016

@author: marzipan
"""

from cardio_noise_removal.utils import get_data, freq_filter
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import normalize, scale

def gen_delta_freqs(signal):
    
    frame_len = 30
    
    low_cut = 1   # TODO must vary with frame length
    high_cut = 14
    
    frames = list()
    for i in range(int(signal.shape[0]/frame_len)-1):
        frames += [signal[(i*frame_len):((i+1)*frame_len),:]]
        
    filtered_frames = list()
    for f in frames:
        filtered_frames += [freq_filter(f,low_cut, high_cut)]
        
    filt_freq_frames = list()
    for f in filtered_frames:
        filt_freq_frames += [np.abs(np.fft.fft(f, axis=0))]
    
    delta_freqs = [0]
    for i in range(len(filt_freq_frames)-1):
        delta_freqs += [np.linalg.norm(filt_freq_frames[i] - filt_freq_frames[i+1])]
        
    x_coords = [frame_len*i for i in range(len(delta_freqs))]
#==============================================================================
#     plt.plot(x_coords, delta_freqs, '-o')
#     plt.plot(f2s(filtered_frames))
#==============================================================================
    
    return filtered_frames
    
def gen_delta_freqs_frames(filtered_frames):
    
    frame_len = filtered_frames[0].shape[0]
        
    filt_freq_frames = list()
    for f in filtered_frames:
        filt_freq_frames += [np.abs(np.fft.fft(f, axis=0))]
    
    delta_freqs = [0]
    for i in range(len(filt_freq_frames)-1):
        delta_freqs += [np.linalg.norm(filt_freq_frames[i] - filt_freq_frames[i+1])]
        
    x_coords = [frame_len*i for i in range(len(delta_freqs))]
    plt.plot(x_coords, delta_freqs, '-o')
    plt.plot(f2s(filtered_frames))
    

# TODO limit delta_freq of super-threshold frames and plot

def filter_delta_freqs(frames):
    '''
    frames: filtered time series frames
    deltas: overall distance frequency magnitude between current and subsequent frames
    '''
    delta_freq_thresh = 200
    
    # Generate list of fft frames
    fft_frames = list()
    for f in frames:
        fft_frames += [np.fft.fft(f, axis=0)]
        
    # Generate list of difference raw delta vecors
    raw_delta_vec = list()
    for i in range(len(fft_frames)-1):
        raw_delta_vec += [fft_frames[i+1] - fft_frames[i]]
    
    # Regenerate raw delta vector based upon threshold-limited difference vectors
    filtered_fft_frames = [fft_frames[0]]
    previous_frame = filtered_fft_frames[0]
    
    for i in range(len(raw_delta_vec)):
        norm = np.linalg.norm(raw_delta_vec[i])
        if norm > delta_freq_thresh:
            print("filtering frame "+str(i)+" with norm "+str(norm))            
            new_delta = raw_delta_vec[i] * (delta_freq_thresh / norm)
        else: 
            new_delta = raw_delta_vec[i]
            
        new_frame = previous_frame + new_delta
        filtered_fft_frames += [new_frame]
        previous_frame = new_frame
    
    # Generate time-domain frames back from filtered fft frames
    
    delta_filtered_td_frames = list()
    for f in filtered_fft_frames:
        delta_filtered_td_frames += [np.fft.ifft(f, axis=0)]
        
    return raw_delta_vec
    
    
def f2s(frames):
    return np.vstack((frames))
    
    
def F(frame):
    return np.fft.fft(frame, axis=0)
  
def iF(frame):
    return np.fft.ifft(frame, axis=0)
    
#TODO constrain delta_freq components individually - track stdev, mean or some such statistic
def rd_std(frame):
    ''' reduce dimensionality via mean+stdev threshold'''
    frame = F(frame)
    mag = np.abs(frame)
    thresh = np.mean(mag) + np.std(mag)
    for i in range(frame.shape[0]):
        if np.abs(frame[i,0]) < thresh:
            frame[i,0] = 0
    return np.fft.ifft(frame, axis = 0)

def rd(frame, num_dims=10): # ~ 6 signal components and 4 noise components
    ''' reduce dimensionality via largest num_dim components'''
    frame = F(frame)
    mag = np.abs(frame)[0:int(len(frame)/2)]
    unordered = list(enumerate(mag))
    ordered = sorted(unordered, key=lambda x : x[1][0], reverse=True)
    pcs = [ordered[i][0] for i in range(num_dims)]
    
    size = frame.shape[0]
    for i in range(size):
        if i in pcs or -(i - size) in pcs:
            pass
        else:
            frame[i,0] = 0
    
    return np.fft.ifft(frame, axis=0), pcs
    
def nplot(frame, x=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if x==None:
        ax.plot(frame)
    else:
        ax.plot(x,frame)

def genWindow():
    fwindow = np.asarray([0,
                          0,
                          0,
                          50,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,
                          0,])
    window = np.zeros((30,1))
    for i in range(15):
        window[i] = fwindow[i]
        window[-i] = fwindow[i].conjugat()
    return window

# TODO apply magnitude 
def normalizeFreqMagProf(frame):
    # TODO search f0 and normalize relative to it
    # TODO Naive: apply fwindow  
    # TODO find characteristic ration between real and imag freq components
    # TODO phase shifts shold be strongly related between frames
    pass

def applyNaiveWindow(frame, window):
    '''
    input: TD frame and FD window
    '''
    frame = F(frame)
    for i in range(len(frame)):
        if np.abs(frame[i]) > window[i]:
            # scale down to fit window
            frame[i] *= window[i] / np.abs(frame[i])
    return np.fft.ifft(frame, axis=0)
    

# Plot frame boundaries
def markFrameBoundaries(frames):
    ymin = -50
    ymax = 30
    frame_count = len(frames)
    frame_len = len(frames[0])
    for x in range(frame_count):
        plt.plot((x*frame_len, x*frame_len), (ymin, ymax), 'k-')
        plt.annotate(str(x),xy=(x*frame_len,ymax))
        
def synthesize(f0, phi, mags, frame_length):
    '''
    output: reasonable FS frame
    '''

    # Extract phi's
    phi0 = phi[0]
    phi1 = phi[1]
    phi2 = phi[2]        
    
    assert(f0 < 0.5)
    assert(phi0 > -np.pi and phi0 < np.pi)
    
    # Init zero'd window
    window = np.zeros((frame_length,1), np.complex128)
    
    # Set base magnitude
#==============================================================================
#     mags = list()
#     mags += [1.0]
#     mags += [mags[0] * 0.75 * 1] 
#     mags += [mags[0] * 0.5 * 1]  
#==============================================================================
    
    # Set phases
    phase = list()
    phase += [phi0]
    phase += [phi1]
    phase += [phi2]
    
    # Create magnitude window
    idxs = list()
    freqs = genFreqs(frame_len=frame_length)
    idxs += [idFreqIdx(freqs, f0)]
    idxs += [idFreqIdx(freqs, 2*f0)]
    idxs += [idFreqIdx(freqs, 3*f0)]
    
    for i in range(len(idxs)):
        for idx, frac in idxs[i]:
            window[idx] = frac * mags[i]
            # Add phase adjustment
            window[idx] = rotateComplexVec(window[idx][0], phase[i])  
            # Add conjugate alias component
            window[-idx] = window[idx].conjugate()
    
    return window

def synthesizeWave(f0, phi=[0,np.pi/3,3*np.pi/4], mags=[40,30,20], frame_length=30, pwr=600):
    '''
    output: reasonable TS frame
    '''
    
    waves = list()
    waves += [ mags[i]*np.sin([(2*np.pi*f0*(i+1)*n/frame_length + phi[i]) for n in range(frame_length)]) for i in range(3)]
    wave = sum(waves)

    # Normalize to desired freq pwr    
    fft = F(wave)
    p = sum(np.abs(fft))
    fft *= pwr/p
    
    return iF(fft)
    
    
#==============================================================================
# def rotateComplexVec(vec, phi):
#     A = np.sqrt(vec.real**2 + vec.imag**2)
#     theta1 = np.arctan2(vec.imag, vec.real)
#     thetaN = addPhase(theta1, phi)
#     x2 = np.cos(thetaN)*A
#     y2 = np.sin(thetaN)*A
#     return np.complex(x2,y2)
#==============================================================================
    
def rotateComplexVec(vec, phi):
    v = np.asarray([[vec.real],[vec.imag]])
    R = np.asarray([[np.cos(phi), -np.sin(phi)],
                    [np.sin(phi), np.cos(phi)]])
    r = np.matmul(R,v)
    return np.complex(r[0],r[1])
    
        

def addPhase(phi0, phi1):
    ''' both arguments should be less than pi'''    
    phi = phi0 + phi1
    sgn = -1 if phi < 0 else 1
    phi = (np.abs(phi) % (2*np.pi))*sgn
    
    if phi < 0:
        if phi < -np.pi:
            phi = (2*np.pi) + phi
    else:
        if phi > np.pi:
            phi = (-2*np.pi) + phi
    return phi
        
def idFreqIdx(freqs, f0):
    #TODO this funciton does not account leackage properly
    #TODO perform fft of unit magnitude pure sinusoid to determine leakage
    for i in range(len(freqs)):
        if np.allclose(f0,freqs[i]):
            return [(i,1.0)]
            
        elif f0 < freqs[i+1]:
            #solve a,b : a * freqs[i] + b * freqs[i+1] = f0
            den = freqs[i+1] - freqs[i]
            Ca = (f0-freqs[i])/den
            Cb = (freqs[i+1]-f0)/den
            return [(i,Ca), (i+1,Cb)]
    raise ("ERROR, frequency not matched.")

def plot3d():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
def angleAnalysis(frame, nd=3):
    rframe,pcs = rd(frame, num_dims=nd)
    pwr = np.abs(F(rframe))
    nplot(pwr)
    for i in pcs:
        ang = np.angle(F(rframe))[i]
        label = "("+str(i)+" , "+str(int(pwr[i]))+") : "+str(ang)
        plt.annotate(label, xy=(i,pwr[i]))
    nplot(rframe)
    
def binaryLocalVx(frame):
    '''
    input: fft frame
    '''
    #TODO find peak in each range, confirm multiples...
    absfft = np.abs(F(frame))[0:int(len(frame)/2)]
    
    peaks_ranges = [
                    (2,4),
                    (5,7),
                    (8,10)]
                    
    peaks = []
    # Find highest value in each range
    for b,e in peaks_ranges:
        peaks += [np.dot( np.asarray([0.5,1,0.5]) ,absfft[b:e+1,0])]
        
    correct_distribution = peaks[0] > peaks[1] and peaks[1] > peaks[2]
    correct_distribution = correct_distribution and peaks[0] < 2*peaks[1]
    
    return correct_distribution
    
def binaryGlobalVx():
    #TODO collect global statistics e.g. pwr
    pass
    
    
def genFreqs(frame_len=30):
    size = frame_len * 1.0
    return [(i/size) if (i < size/2.0) else (-(size-i)/size) for i in range(int(size))]

def printPCs(r):
    for i in range(len(r)):
        if np.abs(F(r))[i] > 0.01:
            print(i,np.abs(F(r))[i], np.angle(F(r))[i])


def annotateXs(ys):
    for i in range(int(len(ys)/2)):
        plt.annotate(str(i),xy=(i,ys[i]))
        
def annotateMaxima(maxima,signal):
    for m in maxima:
        plt.annotate(str(signal[m]),xy=(m,signal[m]))


def generateNoise(theta, pwr, phi, frame_length=30):
    noise = np.sin([(2*np.pi*theta*n/frame_length + phi) for n in range(frame_length)])
    fftnoise = F(noise)
    mag = sum(np.abs(fftnoise))
    fftnoise *= pwr/mag
    return np.reshape(iF(fftnoise), (frame_length,1))

def generateNoisyWave():
    wave = synthesizeWave(2.5)
    noise = generateNoise(2.9,600)
    return wave + noise

from scipy.optimize import minimize

fun = lambda x: (x[0] - 1)**2 + (x[1] - 2.5)**2
cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
        {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2})
bnds = ((0, None), (0, None))
guess = (2, 0)
res = minimize(fun, guess, method='SLSQP', bounds=bnds, constraints=cons)

#==============================================================================
# cons = ({'type': 'ineq', 'fun': lambda x: tolerance[0] - np.abs(x[0] - prev_fo) }, 
#         {'type': 'ineq', 'fun': lambda x: np.pi - np.abs(x[1]) },
#         {'type': 'ineq', 'fun': lambda x: tolerance[1] - np.abs(x[2] - prev_pwr )},
#         {'type': 'ineq', 'fun': lambda x: tolerance[2] - np.abs(x[3] - x[0])},
#         {'type': 'ineq', 'fun': lambda x: np.pi - np.abs(x[4]) },
#         {'type': 'ineq', 'fun': lambda x: tolerance[3] - np.abs(x[5] - missingPwr) })
#==============================================================================

def Sg(x,separate=False, freePhase=False, freeMags=False):
    
    Sfo = x[0]
    Sphi0 = x[1]
    
    if freePhase:
        Sphi1 = x[12]
        Sphi2 = x[13]
    else:
        Sphi1 = Sphi0 + np.pi / 2 #TODO learn per user/session, not per frame
        Sphi2 = Sphi0 + 3 * np.pi / 4
        
    if freeMags:
        mag1 = x[14]
        mag2 = x[15]
    else:
        mag1 = 0.75
        mag2 = 0.5
    
    Spwr = x[2]
    wave = np.reshape(synthesizeWave(Sfo, phi=[Sphi0,Sphi1,Sphi2], mags=[1,mag1,mag2], pwr=Spwr),(30,1))
    
    N1fo = x[3]
    N1phi = x[4]
    N1pwr = x[5]
    noise1 = generateNoise(N1fo,N1pwr,N1phi)
    
    N2fo = x[6]
    N2phi = x[7]
    N2pwr = x[8]
    noise2 = generateNoise(N2fo,N2pwr,N2phi)
    
    N3fo = x[9]
    N3phi = x[10]
    N3pwr = x[11]
    noise3 = generateNoise(N3fo,N3pwr,N3phi)
    
    
    if separate:
        return wave, noise1+noise2+noise3
    else:
        return sum([wave , noise1 , noise2 ,noise3])
        
''' Optimization Routine '''

'''
# GEnerate typical phase statistics
# make assumption and try to hand tune one example...
# Model : min[ ||Sx - Sg||] | Sg = S(fo, phi, pwr) + N(f0, phi, pwr)
# Constrain parameters:
# 1) Sg.fo ~ previous (good SNR)
# 2) Sg.phi = [-pi - +pi]
# 3) Sg.pwr ~ previous (good SNR)
# 4) N.f0 = Accel.f0 ~ Sg.f0
# 5) N.phi = [-pi - +pi]
# 6) N.pwr ~ Sx.pwr - S.pwr

# 1) id peaks and find do len(frame) / inter-peak-interval ~ 3
# 4) +/- 1 * accel.pwr peak ~ Sg.f0
'''

# Get data
data = get_data()
signal = data[:,0]
noise = data[:,4]
frames = gen_delta_freqs(signal)
mags = list()
for f in frames:
    mags += [sum(np.abs(F(f)))[0]]
mags = scale(mags)
    
# Constants - should be defined from context data or best guess w/ large tolerance
tolerance = [0 for i in range(4)]
tolerance[0] = 1.5 # Sfo
tolerance[1] = 1 # Spwr
tolerance[2] = 0.3 # Unused
tolerance[3] = 200 # Npwr

def testMatch(frame, genNoise=False):
    prev_fo = 3        # Either a) TD peak count or b) Signal match optimization
    prev_pwr = 450     # Previous estimate
    #missingPwr = 600   # Total frame pwr - prev_pwr
    
    Sx = frame    # Frame of interest
    
    guess = (3,0,300, # f0,phi,pwr
             3,0,0, 
             3,0,0,
             3,0,0,
             
             np.pi/2,
             np.pi,
             0.75,
             0.5)
    
    # Target function to minimize (i.e. recreate observation)
    fun = lambda x: np.linalg.norm(Sx - Sg(x,freePhase=True, freeMags=True))
    
    cons = ()

    if genNoise:
        noiseLimit = None
    else:
        noiseLimit = .001
    
    bdns = ((prev_fo-tolerance[0], prev_fo+tolerance[0]),
            (-np.pi, np.pi),
            (prev_pwr-tolerance[1], prev_pwr+tolerance[1]),
            
            (.5,5),
            (-np.pi,np.pi),
            (0,noiseLimit),
            (.5,5),
            (-np.pi,np.pi),
            (0,noiseLimit),
            (.5,5),
            (-np.pi,np.pi),
            (0,noiseLimit),

            (-np.pi,np.pi),
            (-np.pi,np.pi),

            (0,0.75),
            (0,0.5))
            
    
    res = minimize(fun, guess, method='SLSQP', bounds=bdns, constraints=cons)
    
    print("score",res['fun'])
    synth = Sg(res['x'])
    sig,noi = Sg(res['x'], separate=True)
    nplot(synth)
    plt.plot(Sx)
    plt.legend(['synthesized','original'])
    
    return sig,noi,res
    
def match(frames):
    
    # Result aggregation variables
    new_frames = list()
    new_pwrs = list()
    new_freqs = list()
    
    # Initial guess
    prev_fo = 3        # Either a) TD peak count or b) Signal match optimization
    prev_pwr = 400     # Previous estimate
        
    for i in range(len(frames)):
        
        Sx = frames[i]    # Frame of interest
        fun = lambda x: np.linalg.norm(Sx - Sg(x))
        
        guess = (prev_fo,0,prev_pwr, # f0,phi,pwr
        
                 3,0,600, # Noise components 
                 3,0,600,
                 3,0,600)
        
        cons = ()

#==============================================================================
#         if mags[i] > 0:
#             # noisy frame
#             noise_power = None
#         else:
#==============================================================================
        noise_power = None
        
        bdns = ((prev_fo-tolerance[0], prev_fo+tolerance[0]),
                (-np.pi, np.pi),
                (prev_pwr-tolerance[1], prev_pwr+tolerance[1]),
                (2,3.5),
                (-np.pi,np.pi),
                (0,noise_power),
                (.5,5),
                (-np.pi,np.pi),
                (0,noise_power),
                (.5,5),
                (-np.pi,np.pi),
                (0,noise_power))
                
        
        res = minimize(fun, guess, method='SLSQP', bounds=bdns, constraints=cons)
        
        # Update context constants
        prev_fo = res['x'][0]  
        #prev_pwr = res['x'][2]
        
        # Aggregate results
        sig,noi = Sg(res['x'], separate=True)
        new_frames += [sig]
        new_pwrs += [prev_pwr]
        new_freqs += [prev_fo]
        
    return new_frames,new_pwrs, new_freqs
        
        
#nframes, npwrs, nfreqs = match(great_frames)
#res = testMatch(frames[1])

# TODO use python filters
# TODO ID good frequency

# TODO ID clean frame and only scale it
#   - use delta freq
#   - use abs freq magnitude
#   - SNR from via main peak dominance 

# Ned good estimate of how much noise there really is before we can ID it.

# TODO Need accurate Phase and Mag constants

import math

def ridgerChild(t0,s):
    def rwav(t):
        return 1/math.sqrt(s)*ridger((t-t0)/s)
    return rwav
    

def ridger(t):
    return -t*math.e**(-(t**2)/2)  

def ridgerWavelet(points, a):
    pass    


'''
Photoplethysmograph Signal Reconstruction based on a Novel Motion Artifact 
Detection-Reduction Approach. Part II: Motion and Noise Artifact Removal'''

