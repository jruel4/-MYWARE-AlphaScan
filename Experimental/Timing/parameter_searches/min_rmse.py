# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 21:30:06 2017

@author: marzipan
"""

from sklearn import linear_model
import pickle
import numpy as np
from matplotlib import pyplot as plt
import timing_utils

offsets = pickle.load(open("..//offsets_4_28_17.p","rb"))
x,y = zip(*offsets)

x,y = timing_utils.clean_data(x,y)
x = np.asarray(x).reshape(-1,1)
y = np.asarray(y).reshape(-1,1)

# Create linear regression object
regr = linear_model.LinearRegression()

#TODO find hour idx
hour_len = 5E5

errors = []

# How much data do we need to calibrate on to get less than 1ms error and hour
# later?
for i in np.linspace(2,5E4,num=50):
    i = int(i)
    
    X_train = x[:i]
    y_train = y[:i]
    
    hour_later = int(i+hour_len)
    
    X_test = x[hour_later:hour_later+100]
    y_test = y[hour_later:hour_later+100]
    
    # Train the model using the training sets
    regr.fit(X_train, y_train)
    
    # Calculate and store rms error
    errors += [(i,np.sqrt(np.mean(regr.predict(X_test) - y_test) ** 2))]


plt.plot(*zip(*errors))





