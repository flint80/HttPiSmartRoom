'''
Created on Oct 21, 2015

@author: avramenko
'''
import httplib
import traceback
from common import util
import threading
import urllib2

import urlparse
import xml.etree.ElementTree as etree

class Openhab():
    '''
    connection to openhab
    '''
    
    def sendJabberMessage(self, msg):
        conn = None
        try:
            fullUrl = "%s?to=%s"%(self.jabberUrl,self.jabberTo)
            parseResult = urlparse.urlparse(fullUrl)
            server = parseResult.netloc
            conn = httplib.HTTPConnection(server)
            path = "%s?%s" % (parseResult.path, parseResult.query)
            conn.request('POST', path, msg)
            result = conn.getresponse()
            util.logger.debug("result.status = %s, result.reason = %s" % (result.status, result.reason))
        except:
            util.logger.error("unable to send message: %s" , traceback.format_exc())
        finally:
            if conn:        
                conn.close()
                
    def doQueryOpenhab(self,queryUrl):
        conn = urllib2.urlopen(queryUrl)
        try:
            content = conn.read()
            self.sendJabberMessage(content)
        finally:        
            conn.close()
                    
    def doProcess(self, body):
        if body.startswith("items"):
            openhabUrl = "%s/rest/items"%(self.openhabUrl)
            conn = urllib2.urlopen(openhabUrl)
            try:
                content = conn.read()
                tree = etree.fromstring(content)
                result = ""
                for item in tree:
                    for elm in item:
                        if elm.tag == "name":
                            result = result+"\n"+elm.text+"="
                        if elm.tag == "state":
                            result = result+elm.text                         
                self.sendJabberMessage(result.strip())
            finally:        
                conn.close()
            return 
        if body.startswith("status"):
            itemName = body[6:].strip()
            openhabUrl = "%s/rest/items/%s"%(self.openhabUrl, itemName)
            conn = urllib2.urlopen(openhabUrl)
            try:
                content = conn.read()
                tree = etree.fromstring(content)
                result = ""
                for elm in tree:
                    if elm.tag == "name":
                        result = result+elm.text+"="
                    if elm.tag == "state":
                        result = result+elm.text                         
                self.sendJabberMessage(result.strip())
            finally:        
                conn.close()
            return  
    
    
    def setValue(self, queryParams, body):
        if body.startswith('items') or body.startswith('status'):
            h = threading.Thread(target=self.doProcess, args = {body})
            h.setDaemon(True)
            h.start()        
            
    def __init__(self, params):
        '''
        Constructor
        '''
        self.openhabUrl = params['openhabUrl']
        self.jabberUrl = params['jabberUrl']
        self.jabberTo = params['jabberTo']
        
        
        
    
           
