#!/bin/bash -x

tftp 192.168.1.105 69 << TST
binary << TST
put firmware/AlphaScanFirmware.bin firmware.bin
