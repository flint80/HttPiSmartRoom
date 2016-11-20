'''
Created on Oct 20, 2015

@author: avramenko
'''
import sys
import os

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "libs"))

from server.http import HttpServerConfiguration, HttpServer
import httplib
import threading
import time
import common.util as util
from drivers import registry as driversRegistry
import logging
import traceback


httpConfig = None
def isServerRunning():
    global httpConfig
    conn = None 
    try:
        conn = httplib.HTTPConnection("localhost:%s" % httpConfig.port)
        conn.request('GET', '/check')
        time.sleep(1)
        return True
    except:
        pass
    finally:
        if conn:
            conn.close()    
    return False

def stopServer():
    global httpConfig   
    conn = None 
    try:
        conn = httplib.HTTPConnection("localhost:%s" % httpConfig.port)
        conn.request('GET', '/stop')
        time.sleep(1)
    except:
        print "unable to stop server %s" % traceback.format_exc()
    finally:
        if conn:
            conn.close()    
def printServerRunning():
    
    while not isServerRunning():
        time.sleep(1)
    util.logger.info("server started")

def main(args):
    global httpConfig    
    # configuring logger
    if not os.path.exists("temp"):
        os.mkdir("temp")
    try:
        # preparing http config
        httpConfig = HttpServerConfiguration()
        config = util.readConfig('config.cfg')
        httpConfig.port = int(config['port'])
        for arg in args:
            if arg == 'stop':
                stopServer()
                return
        logging.basicConfig(filename='temp/smartroom.log', filemode='a', format='%(asctime)-15s %(levelname)6s: %(message)s', level=logging.DEBUG)
        # initializing handlers registry
        for entry in os.listdir('devices'):
            fileName = "devices/%s" % entry
            if os.path.isfile(fileName):
                util.logger.debug("analyzing device config %s" % fileName)
                deviceConfig = util.readConfig(fileName)
                name = deviceConfig['name']
                enabled = True 
                if "enabled" in deviceConfig:
                    enabled = "true" == deviceConfig["enabled"]
                
                if enabled:
                    deviceType = deviceConfig['type']
                    driverClass = driversRegistry[deviceType]
                    driverInstance = driverClass(deviceConfig)
                    httpConfig.mapping[name] = driverInstance
                    util.logger.info("device %s was successfully registered" % name)
        
        # stop running server
        wasRunning = False
        while isServerRunning():
            if not wasRunning:
                util.logger.debug("instance of server is already running, trying to stop it")
            wasRunning = True
            stopServer()
            time.sleep(1)
        if wasRunning:
            util.logger.info("previous instance of server was stopped")
            
        # start web server        
        h = threading.Thread(target=printServerRunning)
        h.setDaemon(True)
        h.start()
        HttpServer(httpConfig)
    except:
        print "unable to start server %s" % traceback.format_exc()
        util.logger.error("unable to start server %s" , traceback.format_exc())
        
main(sys.argv)        