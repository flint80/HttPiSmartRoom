'''
Created on Oct 21, 2015

@author: avramenko
'''
from common import util
import xmpppy2
import httplib
from urlparse import urlparse
import urllib
import traceback
import threading
import time
import schedule2


class Jabber():
    '''
    send jabber messages, listen to incomming messages
    '''
    
    def resetConnection(self):
        self.conn = None
        util.logger.debug("connection was reset")
        
    def messageHandler(self,conn, mess):
        body = mess.getBody()
        if body == None:
            return
        conn2 = None
        try:
            additionalParams = dict()
            additionalParams['from'] = "%s@%s" % (mess.getFrom().getNode(), mess.getFrom().getDomain())
            fullUrl = "%s?%s" % (self.url, urllib.urlencode(additionalParams))
            parseResult = urlparse(fullUrl)
            server = parseResult.netloc
            conn2 = httplib.HTTPConnection(server)
            path = "%s?%s" % (parseResult.path, parseResult.query)
            conn2.request('POST', path, body)
            result = conn2.getresponse()
            util.logger.debug("result.status = %s, result.reason = %s" % (result.status, result.reason))
        except:
            util.logger.error("unable to handle message: %s" , traceback.format_exc())
        finally:
            if conn2:        
                conn2.close()
    def doSendPresence(self):
        self.updateConnection()
        try:
            self.conn.sendPresence()
        except:
            util.logger.error("unable to send presence %s" , traceback.format_exc())
            self.resetConnection()
                
    def updateConnection(self):
        if self.conn:
            return
        jid = xmpppy2.JID(self.jid)
        util.logger.debug("jabber: creating client")
        self.conn = xmpppy2.Client(jid.getDomain(), debug = [])
        self.conn.UnregisterDisconnectHandler(self.conn.DisconnectHandler)
        self.conn.RegisterDisconnectHandler(self.resetConnection)
        util.logger.debug("jabber: connecting")
        conn_result = self.conn.connect()
        if not conn_result:
            raise ValueError("Can't connect to server %s" % jid.getDomain())
        auth_result = self.conn.auth(jid.getNode(), self.passwd)
        if not auth_result:
            util.logger.error("Can't authorize with %s" % jid.getNode())
            return
        self.conn.RegisterHandler('message', self.messageHandler)
        util.logger.debug("jabber: sending init presence")
        self.conn.sendInitPresence()
        util.logger.debug("jabber: authorization completed")
                
    def doSendPresenceJob(self):
        time.sleep(20)
        scheduler = schedule2.Scheduler()
        scheduler.every(10).minutes.do(self.doSendPresence)
        while not self.toBeStopped:
            try:
                scheduler.run_pending()
            except:
                util.logger.error("unable to execute job %s" , traceback.format_exc())
                print "unable to execute job %s" % traceback.format_exc()
            time.sleep(1)            
                
    def doPoll(self):
        util.logger.debug("jabber: sleeping")
        time.sleep(20)
        while not self.toBeStopped:
            try:
                self.updateConnection()
                self.conn.Process(1)
            except:
                util.logger.warning("error occured while polling jabber %s" % traceback.format_exc() )
                self.resetConnection()
                time.sleep(10)
        util.logger.debug("polling ended" )   

    def __init__(self, params):
        '''
        Constructor
        '''
        self.url = params['url']
        self.jid = params['jid']
        self.passwd = params['password']
        self.toBeStopped = False
        self.conn = None
        h = threading.Thread(target=self.doPoll)
        h.setDaemon(True)
        h.start()
        h2 = threading.Thread(target=self.doSendPresenceJob)
        h2.setDaemon(True)
        h2.start()
            
    def stop(self):
        self.toBeStopped = True
        try:
            self.conn.disconnected()
        except:
            pass        
            
    def setValue(self, queryParams, body):
        toAddress = queryParams['to']
        self.conn.send(xmpppy2.Message(xmpppy2.JID(toAddress), body))
        util.logger.debug("xmpp message to %s: %s" % (toAddress, body))
