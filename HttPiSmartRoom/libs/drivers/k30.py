# -*- coding: utf-8 -*-
'''
Created on 20 нояб. 2016 г.

@author: avramenko
'''

from common import util
import serial
import time

class K30():
    
    def getValue(self, queryParams):
        ser = serial.Serial(self.device,baudrate =9600,timeout = .5)
        try:
            ser.flushInput()
            time.sleep(1)
            ser.flushInput()
            ser.write("\xFE\x44\x00\x08\x02\x9F\x25")
            time.sleep(.5)
            resp = ser.read(7)
            high = ord(resp[3])
            low = ord(resp[4])
            co2 = (high*256) + low
            return "%s" % co2
        finally:
            ser.close()
            
            
            
    
    def __init__(self, params):
        '''
        Constructor
        '''
        if "device" in params:
            self.device = params["device"]
        else:
            self.device = "/dev/ttyAMA0"
        util.logger.debug("k30 is attached as %s" %self.device)
        
                