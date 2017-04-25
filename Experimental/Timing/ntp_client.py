# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 15:48:13 2017

@author: marzipan
"""

import ntplib
from time import ctime

c = ntplib.NTPClient()

response = c.request('127.0.0.1', version=3)
response.offset

response.version

ctime(response.tx_time)

ntplib.leap_to_text(response.leap)

response.root_delay

ntplib.ref_id_to_text(response.ref_id)
