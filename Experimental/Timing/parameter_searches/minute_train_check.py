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

offsets = pickle.load(open("..//TimeSync_test.p","rb"))
x,y = zip(*offsets)

x,y = timing_utils.clean_data(x,y)
x = np.asarray(x).reshape(-1,1)
y = np.asarray(y).reshape(-1,1)

# Create linear regression object
regr = linear_model.LinearRegression()

hour_len = 5E5
min_len = 6000

X_train = x[:6000]
y_train = y[:6000]
# Train the model using the training sets
regr.fit(X_train, y_train)
errors = []

# How much data do we need to calibrate on to get less than 1ms error and hour
# later?
for i in np.linspace(6000,len(x)-101,num=(((len(x)-6000)/100))):
    i = int(i)
    
    X_test = x[i:i+100]
    y_test = y[i:i+100]
    
    # Calculate and store rms error
    errors += [(i,np.sqrt(np.mean(regr.predict(X_test) - y_test) ** 2))]


plt.plot(*zip(*errors))





