# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 22:00:26 2017

@author: marzipan
"""

import os
import matplotlib

if 'QT_API' not in os.environ and 'ETS_TOOLKIT' not in os.environ: 
    os.environ['QT_API'] = 'pyqt'
    os.environ['ETS_TOOLKIT'] = 'qt4'

matplotlib.get_backend()

# get available
matplotlib.rcsetup.interactive_bk
matplotlib.rcsetup.non_interactive_bk
matplotlib.rcsetup.all_backends


#http://cyrille.rossant.net/making-pyqt4-pyside-and-ipython-work-together/