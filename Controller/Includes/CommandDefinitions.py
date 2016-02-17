# -*- coding: utf-8 -*-
"""
Created on Sat Feb 06 15:36:27 2016

@author: marzipan
"""

# Declare command dict
TCP_COMMAND = dict()
command_index = 0

def addCommand(name):
    global TCP_COMMAND, command_index
    TCP_COMMAND[name] = command_index
    command_index += 1

###############################################################################    
# General 
###############################################################################
addCommand("GEN_update_cmd_map") #NOTE: this must ALWAYS be first i.e. 0x00
addCommand("GEN_get_status")
addCommand("GEN_start_ota")
addCommand("GEN_start_ap")
addCommand("GEN_get_dev_ip")
addCommand("GEN_listen_beacon")
addCommand("GEN_get_sys_params")

###############################################################################
# ADC
###############################################################################
addCommand("ADC_start_stream")
addCommand("ADC_stop_stream")
addCommand("ADC_get_register")
addCommand("ADC_update_register")
addCommand("ADC_set_udp_delay")

###############################################################################
# POWER
###############################################################################
addCommand("PWR_get_status")

###############################################################################
# ACCEL
###############################################################################
addCommand("ACC_get_status")

###############################################################################
# SPIFFS
###############################################################################
addCommand("FS_format_fs")
addCommand("FS_get_net_params")
addCommand("FS_get_fs_info")
addCommand("FS_get_command_map")





