'''
Created on Oct 21, 2015

@author: avramenko
'''
import RPIO
from common import util

class GPIO():
    '''
    reads temperature value from sensor ds18b20
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        self.pin =  int(params["pin"])
        RPIO.setup(self.pin, RPIO.OUT, initial=RPIO.LOW)
        self.value = 0
        
    def stop(self):
        RPIO.cleanup()
            
    def setValue(self, queryParams, body):
        value = body
        if "value" in queryParams:
            value =queryParams["value"]
        if "1" == value:
            RPIO.output(self.pin, 1)
            util.logger.debug("pin %s set to 1" % (self.pin))
            self.value = 1
            return
        if "0" == value:
            RPIO.output(self.pin, 0)
            util.logger.debug("pin %s set to 0" % (self.pin))
            self.value = 1
            return
    def getValue(self, queryParams):
        return "%s" % (self.value)        
