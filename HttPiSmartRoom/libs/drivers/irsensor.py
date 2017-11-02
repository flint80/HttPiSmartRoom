# -*- coding: utf-8 -*-
'''
Created on 20 нояб. 2016 г.

@author: avramenko
'''

import lirc
import httplib
import urlparse
from common import util
import traceback
import threading

class IRSensor():
    
    def stop(self):
        self.toBeStopped = True
    
    def pollIR(self):
        try:
            util.logger.debug("initializing lirc ")
            lirc.init("HttPiSmartroom",  blocking=True)
            util.logger.debug("loading config ")
            lirc.load_config_file("/home/pi/.lircrc")
            util.logger.debug("config loaded")
            while True:
                if(self.toBeStopped):
                    lirc.deinit()    
                    break;
                codeIR = lirc.nextcode()
                util.logger.debug("get code %s " % codeIR)
                try:
                    if codeIR in self.keyMap:
                        url = self.keyMap[codeIR]
                        util.logger.debug("found mapping %s " % url)            
                        parseResult = urlparse.urlparse(url)
                        server = parseResult.netloc
                        conn = httplib.HTTPConnection(server)
                        path = "%s?%s" % (parseResult.path, parseResult.query)
                        conn.request('POST', path)
                        conn.getresponse()
                except:
                    util.logger.error("unable to send ir command %s: %s" % (codeIR, traceback.format_exc()))
        except:       
            util.logger.error("error polling lirc %s" % traceback.format_exc())
            
            
            
    
    def __init__(self, params):
        '''
        Constructor
        '''
        self.toBeStopped=False
        self.keyMap = {}
        for key in params:
            if key.startswith('key.'):
                self.keyMap[key[len('key.')+1:]] = params[key]
        h = threading.Thread(target=self.pollIR)
        h.setDaemon(True)
        h.start()
        util.logger.debug("thread started")
        
                