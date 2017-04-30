# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 18:03:50 2017

@author: marzipan
"""

from sklearn import linear_model
import pickle
import numpy as np
from matplotlib import pyplot as plt

# Given a large quantity of samples, the question is how many sample do we need to
# train on until the accuracy on the dataset as a whole is sufficient?
offsets = pickle.load(open("offsets_4_28_17.p","rb"))
x,y = zip(*offsets)
x = np.asarray(x).reshape(-1,1)
y = np.asarray(y).reshape(-1,1)

# Create linear regression object
regr = linear_model.LinearRegression()

# TODO we cannot have a single precision go under 1ms, so let's test on the 
# last N data points to make sure they perform sufficiently well.
# i.e. get a measurement of maximum error

# TODO we want to make sure that the root mean square error is under 1000
# np.sqrt(np.mean(regr.predict(cxt) - cxy) ** 2)

X_test = cxt[-1000:]
y_test = cxy[-1000:]
scores = []
for i in np.linspace(2,1E6,num=30):
    i = int(i)
    # iteratively break the data into train and test sets, collecting the error
    # scores as we progress
    X_train = cxt[:i]
    y_train = cxy[:i]
    
#==============================================================================
#     X_test = x[i:]
#     y_test = y[i:]
#==============================================================================
    
    # Train the model using the training sets
    regr.fit(X_train, y_train)

    score = regr.score(X_test, y_test)
    scores += [(i,score)]    

    # Explained variance score: 1 is perfect prediction
    #print('Variance score: %.2f' % score)

plt.plot(*zip(*scores))





