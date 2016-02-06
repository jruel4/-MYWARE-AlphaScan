# -*- coding: utf-8 -*-
"""
Created on Sat Feb 06 15:36:27 2016

@author: marzipan
"""

TCP_COMMAND = dict()
command_index = 0

def addCommand(name):
    global TCP_COMMAND, command_index
    TCP_COMMAND[name] = command_index
    command_index += 1

###############################################################################    
# General 
###############################################################################
addCommand("GEN_get_status")
addCommand("GEN_start_ota")

###############################################################################
# ADC
###############################################################################
addCommand("ADC_start_stream")
addCommand("ADC_stop_stream")
addCommand("ADC_get_register")
addCommand("ADC_update_register")

###############################################################################
# ACCEL
###############################################################################
addCommand("ACC_get_status")

###############################################################################
# POWER
###############################################################################
addCommand("PWR_get_status")




# TODO add matching command schema to firmware






