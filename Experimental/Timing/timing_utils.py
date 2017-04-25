# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 18:47:37 2017

@author: marzipan
"""

from decimal import Decimal

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