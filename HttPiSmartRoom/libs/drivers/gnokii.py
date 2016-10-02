'''
Created on Oct 21, 2015

@author: avramenko
'''
import subprocess
from common import util
from datetime import  datetime
import time
import traceback

class Gnokii():
    '''
    reads temperature value from sensor ds18b20
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        self.testMode = 'test-mode' in params and 'True' == params['test-mode']
        errorCount = 0
        if not self.testMode and errorCount < 5:
            try:
                gnokiiData = subprocess.Popen(['gnokii', '--identify'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = gnokiiData.communicate()
                out_decode = out.decode('utf-8')
                lines = out_decode.split('\n')
                util.logger.debug("gnokii --identify stdout: %s \n stderr %s " % (out_decode, err.decode('utf-8')))
                if not lines:
                    raise ValueError("unable to communicate with phone")
                return
            except:
                util.logger.error("unable to start gnokii %s", traceback.format_exc())
                time.sleep(10)
                errorCount = errorCount +1
    def setValue(self, queryParams, body):
        phoneNumber = queryParams['phone']
        if self.testMode:
            dt = datetime.now()
            f = open("temp/msg-%s-%s-%s-%s-%s-%s.txt" % (phoneNumber, dt.month, dt.day, dt.hour, dt.minute, dt.second), 'w')
            try:
                f.write(body)
                return
            finally:
                f.close()
        gnokiiData = subprocess.Popen(["echo '%s' | gnokii --sendsms %s" % (body, phoneNumber)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
        out, err = gnokiiData.communicate()
        out_decode = out.decode('utf-8')
        util.logger.debug("gnokii --sendsms  stdout: %s \n stderr %s " % (out_decode, err.decode('utf-8')))
