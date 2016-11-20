'''
Created on Oct 21, 2015

@author: avramenko
'''
import Adafruit_DHT
import threading


class DHT22():
    '''
    works with temperature and humidity sensor DHT22
    '''
    
    lock = threading.Lock()
    
    def __init__(self, params):
        '''
        Constructor
        '''
        self.pin = int(params['pin'])
        self.sensor = params['sensor']
                
    def getValue(self, queryParams):
        self.lock.acquire()
        try:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
            if self.sensor == 'temperature':
                return temperature
            return humidity
        finally:
            self.lock.release()

