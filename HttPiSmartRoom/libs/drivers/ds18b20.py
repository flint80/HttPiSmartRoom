'''
Created on Oct 21, 2015

@author: avramenko
'''
import os
import subprocess
import time
from common import util

class Ds18b20():
    '''
    reads temperature value from sensor ds18b20
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        self.file = params['file']
        if not os.path.exists(self.file):
            raise ValueError("temperature sensor is not available at %s" % self.file)
    
    def _read_temp_raw(self):
        os_name = os.name
        if os_name == "posix":
            catdata = subprocess.Popen(['cat',self.file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = catdata.communicate()[0]
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            return lines
        f = open(self.file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def getValue(self, queryParams):
        cnt = 0
        found = False
        while cnt < 5:
            cnt = cnt +1
            lines = self._read_temp_raw()
            if lines[0].strip()[-3:] == 'YES':
                found = True
                break
            time.sleep(0.2)
        if found:    
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
        response = ""
        for line in lines:
            response = response + "\n"+ line
        util.logger.error("unable to get temperature data from sensor, response: \n %s" % response)
        raise ValueError("unable to get temperature data from sensor") 
            
    
            