'''
Created on Oct 21, 2015

@author: avramenko
'''
import RPi.GPIO as GPIO
from utils import util

class GPIO():
    '''
    reads temperature value from sensor ds18b20
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        self.pin =  int(params["pin"])
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self.value = 0
        
    def stop(self):
        GPIO.cleanup()
            
    def setValue(self, queryParams, body):
        value = body
        if "value" in queryParams:
            value =queryParams["value"]
        if "1" == value:
            GPIO.output(self.pin, 1)
            util.logger.debug("pin %s set to 1" % (self.pin))
            self.value = 1
            return
        if "0" == value:
            GPIO.output(self.pin, 0)
            util.logger.debug("pin %s set to 0" % (self.pin))
            self.value = 1
            return
    def getValue(self, queryParams):
        return "%s" % (self.value)        
