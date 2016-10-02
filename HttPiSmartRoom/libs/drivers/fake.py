'''
Created on Oct 21, 2015

@author: avramenko
'''
import os

class FakeDevice():
    '''
    Can Read value from file
    Can Write value to file
    '''
    
    READ_OPERATION_NAME = 'READ'
    WRITE_OPERATION_NAME = 'WRITE'
    
    
    

    def __init__(self, params):
        '''
        Constructor
        '''
        self.operation = params['operation']
        if self.operation != FakeDevice.READ_OPERATION_NAME and self.operation != FakeDevice.WRITE_OPERATION_NAME:
            raise ValueError("unsupported operation %s" % self.operation)
        self.file = params['file']
    
    
    def getValue(self, queryParams):
        if self.operation == FakeDevice.WRITE_OPERATION_NAME:
            raise ValueError("getValue is not supported for WRITE Device Type")
        if not os.path.exists(self.file):
            return "-1"
        f = open(self.file, 'r')
        try:
            line = f.readline()
            if not line:
                return '-1'
            return line.strip()
        finally:
            f.close()
            
    def setValue(self, queryParams, body):
        if self.operation == FakeDevice.READ_OPERATION_NAME:
            raise ValueError("setValue is not supported for READ Device Type")
        f = open(self.file, 'w')
        try:
            f.write(body)
        finally:
            f.close()
            