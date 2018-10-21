# -*- coding: utf-8 -*-
'''
Created on 20 нояб. 2016 г.

@author: avramenko
'''

from utils import util
import threading
import serial
import time
import traceback


class Arduino():
    
    
    def getValue(self, queryParams):
        if not self.serial:
            return "error";
        lock = threading.Lock();
        lock.acquire()
        try:
            cmd=queryParams['command']
            if not cmd or not cmd[0]:
                raise Exception("no command specified")
            self.serial.writelines(cmd[0]+"|")
            time.sleep(1)
            resp = self.serial.readline();
            #ser.flushOutput()
            return resp.strip()
        finally:
            lock.release()
            
    def setValue(self, queryParams,body):
        if not self.serial:
            raise Exception("serial is unavailable")
        lock = threading.Lock();
        lock.acquire()
        try:
            cmd=queryParams['command']
            if not cmd:
                raise Exception("no command specified")
            self.serial.write(cmd+"\n")
            time.sleep(1)
        finally:
            lock.release()
                    
    def doAction(self):
        lastTime = time.time()
        while not self.isToBeStopped:
            if time.time()-lastTime > 60:
                lastTime = time.time()
                self.checkSerial();
            time.sleep(0.5)        
                
            
    def checkSerial(self):
        lock = threading.Lock();
        lock.acquire()
        try:
            if self.serial:
                params={}
                params['command']="t"
                try:
                    self.getValue(params)
                    return
                except:
                    util.logger.warning("arduino serial check fails, reason %s"  % traceback.format_exc()  )            
                    
            try:
                self.serial = serial.Serial(self.device,baudrate =9600,timeout = 5)
                util.logger.warning("reopened main serial %s"  % self.device  )
                return
            except:
                util.logger.warning("unable to open main serial %s, reason %s"  % (self.device, traceback.format_exc())  )
                if self.altdevice:
                    try:
                        self.serial = serial.Serial(self.altdevice,baudrate =9600,timeout = 5)
                        util.logger.warning("reopened alternative serial %s"  % self.altdevice  )
                    except:
                        util.logger.warning("unable to open alternative serial %s, reason %s"  % (self.altdevice, traceback.format_exc())  )
                        self.serial = None
        finally:
            lock.release()    
                
    def stop(self):
        self.isToBeStopped = True
        try:
            self.serial.close();
        except:
            pass         
    
    def __init__(self, params):
        '''
        Constructor
        '''
        self.isToBeStopped = False
        self.serial = None
        if "device" in params:
            self.device = params["device"]
        else:
            self.device = "/dev/ttyUSB0"
        if "alternative-device" in params:
            self.altdevice = params["alternative-device"]
        self.checkSerial()
        if self.serial:
            util.logger.debug("successfully connected to arduino")
        else:
            util.logger.warning("unable to connect to arduino")    
        h = threading.Thread(target=self.doAction)
        h.setDaemon(True)
        h.start()    
            
        
                