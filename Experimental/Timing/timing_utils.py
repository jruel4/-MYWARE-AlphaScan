# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 18:47:37 2017

@author: marzipan
"""

from decimal import Decimal
from scipy import stats
from scipy.stats import mstats
import numpy as np

def s2us(s):
    return int((s*1E6)//1)


def get_scientific(p):
 return '%.2E' % Decimal(str(p))
 
def get_offset_us(t1,t2,t3,t4):
    '''
    Input: timestamps in microseconds
    Output: clock offset in microseconds
    # Clock Offset = ((t2-t1)+(t3-t4))/2
    '''
    return int((((t2-t1)+(t3-t4))/2.0)//1)
    
def get_iqr(vals):
    quantiles = mstats.mquantiles(vals)
    return quantiles[2]-quantiles[0]

def get_trimmed_mean(vals):
    return stats.trim_mean(vals,.25)
    
def clean_data(x,y,wlen = 250):
    cx = []; cy = [];
    
    # loop over 250 sample segments and filter them each...
    rng = np.linspace(0,len(x),num=(len(x)/wlen))
    for i in range(len(rng)-1):
        b=int(rng[i]);e=int(rng[i+1]);
        q75, q25 = np.percentile(y[b:e], [75 ,25])
        for i in range(b,e):
            if (y[i] < q75) and (y[i] > q25):
                cx += [x[i]]
                cy += [y[i]]
    return cx,cy
            
            
            
            
            
            
            
            
            
            
            
            
            
            