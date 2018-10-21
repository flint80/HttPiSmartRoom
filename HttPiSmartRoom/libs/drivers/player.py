'''
Created on Oct 21, 2015

@author: avramenko
'''
from mpd import MPDClient

class MPD():
    '''
    Can Stop/Play selected song
    '''
    
    TOGGLE_OPERATION = 'TOGGLE'
    VOLUMEUP_OPERATION = 'VOLUMEUP'
    VOLUMEDOWN_OPERATION = 'VOLUMEDOWN'
    
    
    

    def __init__(self, params):
        '''
        Constructor
        '''
        if "songpos" in params:
            self.songpos = int(params['songpos'])
        else:
            self.songpos = 0
                
        self.server = params['server']

            
    def setValue(self, queryParams, body):
        op = queryParams['op']
        if op == self.TOGGLE_OPERATION:
            client = MPDClient()               # create client object
            client.timeout = 10                # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
            client.connect(self.server, 6600)  # connect to localhost:6600
            try:
                status = client.status()
                if status['state'] == 'play':
                    client.stop()
                else:
                    client.play(self.songpos)    
            finally:        
                client.close()                     # send the close command
                client.disconnect()
        elif op == self.VOLUMEUP_OPERATION:
            client = MPDClient()               # create client object
            client.timeout = 10                # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
            client.connect(self.server, 6600)  # connect to localhost:6600
            try:
                status = client.status()
                volume = int(status['volume'])
                if volume <=80:
                    client.setvol(volume+20)
                else:
                    client.setvol(100)     
            finally:        
                client.close()                     # send the close command
                client.disconnect()       
        elif op == self.VOLUMEDOWN_OPERATION:
            client = MPDClient()               # create client object
            client.timeout = 10                # network timeout in seconds (floats allowed), default: None
            client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
            client.connect(self.server, 6600)  # connect to localhost:6600
            try:
                status = client.status()
                volume = int(status['volume'])
                if volume > 20:
                    client.setvol(volume-20)
                else:
                    client.setvol(0)     
            finally:        
                client.close()                     # send the close command
                client.disconnect()                     
        else:
            raise ValueError("unsupported operation %s" % op)