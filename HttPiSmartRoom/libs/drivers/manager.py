'''
Created on Oct 21, 2015

@author: avramenko
'''
import httplib
import traceback
from utils import util
import time
import threading
from datetime import datetime as dt, datetime
import schedule2
import urllib2
import sqlite3 as lite
import os
import sqlite3
import urlparse

class Manager():
    '''
    drives application
    '''
    
    sensorsNames = ('ta', 'tb')
    powerFileName = 'power.dat'
    timeFormat = "%Y-%m-%d-%H:%M:%S"
    databaseName = "temp/temperature.db"
    
    
    def sendSms(self, message):
        conn = httplib.HTTPConnection("localhost:%s" % self.httpPort)
        try:
            msg = message
            if len(msg) > 150:
                msg = msg[:150]
                util.logger.warn("sms was truncated to %s" % msg)
            conn.request('POST', "/write/sms?phone=%s" % self.phoneNumber, msg)
            result = conn.getresponse()
            util.logger.debug("result.status = %s, result.reason = %s" % (result.status, result.reason))
        except:
            util.logger.error("unable to stop server %s" , traceback.format_exc())
        finally:        
            conn.close()
    def getTemperature(self, sensorName):
        conn = urllib2.urlopen("http://localhost:%s/read/%s" % (self.httpPort, sensorName))
        try:
            content = conn.read()
            return float(content)
        finally:        
            conn.close()
                              
    def getTemperatures(self):
        result = dict()
        for sensorName in Manager.sensorsNames:
            result[sensorName] = self.getTemperature(sensorName)
        return result
    
    def checkCorrectStop(self):
        content = util.readTempFile(Manager.powerFileName)
        now = dt.now()
        util.writeTempFile(Manager.powerFileName, now.strftime(Manager.timeFormat))
        if content is None:
            util.logger.debug("server was stopped correctly")
            return
        message= "ERROR: no electricity from %s to %s" % (content, now.strftime(Manager.timeFormat))
        util.logger.debug("server was not stopped correctly stopped, sending message: %s" % message)
        self.sendSms(message)
    
    def updatePowerFile(self):
        now = dt.now()
        util.writeTempFile(Manager.powerFileName, now.strftime(Manager.timeFormat))
        
    def checkTemperatureTrigger(self):
        try:
            currentTemperatures = self.getTemperatures()
            errorMessage = ""
            okMessage = ""
            for sensorName in Manager.sensorsNames:
                currentTemperature = currentTemperatures[sensorName]
                minTemperature = self.tmins[sensorName]
                fileName = "%s.val" % sensorName
                if minTemperature > currentTemperature:
                    content = util.readTempFile(fileName)
                    if content ==None or float(content) >  minTemperature:
                        errorMessage = errorMessage + ("%s (%s) < %s." % (sensorName, content, minTemperature))
                if minTemperature < currentTemperature:
                    content = util.readTempFile(fileName)
                    if content and float(content) <  minTemperature:
                        okMessage = okMessage + ("%s (%s)> %s." % (sensorName, content, minTemperature))        
                util.writeTempFile(fileName, "%s" % currentTemperature)        
            if errorMessage != '':
                self.sendSms("ERROR: %s" % errorMessage)
            if okMessage != '':
                self.sendSms("OK: %s" % okMessage)
        except:
            util.logger.error("unable to check temperature trigger: %s" , traceback.format_exc())        
    
    def sendJabberMessage(self, msg):
        conn = None
        try:
            parseResult = urlparse.urlparse(self.jabberUrl)
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
    def doShow(self, sensorName):
        temp = self.getTemperature(sensorName)
        self.sendJabberMessage("%s" % temp)
            
    def setValue(self, queryParams, body):
        if body.startswith('show'):
            sensorName = body[4:].strip()
            h = threading.Thread(target=self.doShow, args = {sensorName: [1]})
            h.setDaemon(True)
            h.start()
                
    def updateTemperatureHistory(self):
        try:
            if not os.path.exists(Manager.databaseName):
                self.initTemperatureDatabase()
            currentTemperatures = self.getTemperatures()
            con = lite.connect(Manager.databaseName, detect_types=sqlite3.PARSE_DECLTYPES)
            with con:
                now = datetime.now()
                for sensorName in Manager.sensorsNames:
                    currentTemperature = currentTemperatures[sensorName]
                    cur = con.cursor()    
                    cur.execute("INSERT INTO temperature(sensorName, regDate, value, reported) values (?, ?, ?,?)", (sensorName, now, currentTemperature,0))
            con.commit()
            util.logger.debug("temperature history was updated")        
        except:
            util.logger.error("error occured while updating temperature history: %s" % traceback.format_exc())        
            
    def reportTemperatureHistory(self):
        if not os.path.exists(Manager.databaseName):
            return
        try:
            data = dict()           
            con = lite.connect(Manager.databaseName, detect_types=sqlite3.PARSE_DECLTYPES)
            ids = []
            with con:
                for sensorName in Manager.sensorsNames:
                    cur = con.cursor()
                    cur.execute("SELECT Id, regDate, value FROM temperature WHERE sensorName = ?  and reported != ? order by regDate asc", (sensorName, 1))
                    rows = []
                    for row in cur.fetchall():
                        rows.append(row)
                        ids.append(row[0])
                    data[sensorName] = rows
            result = ""
            for sensorName in Manager.sensorsNames:
                result = result+("%s." % sensorName)
                for row in data[sensorName]:
                    result = result +"%s-%s" % (row[1].hour, row[2])
            self.sendSms(result)
            query = ""
            for rowId in ids:
                if len(query) > 0:
                    query = query+"OR "
                query = query + "Id = '%s'" % rowId    
            if len(query) >0:    
                con = lite.connect(Manager.databaseName, detect_types=sqlite3.PARSE_DECLTYPES)
                with con:
                    cur = con.cursor()    
                    cur.execute("UPDATE temperature set reported = 1 where %s" % query)
                    con.commit()
        except:
            util.logger.error("error occured while reporting temperature history: %s" % traceback.format_exc())            
        
    def initTemperatureDatabase(self):
        con = lite.connect(Manager.databaseName, detect_types=sqlite3.PARSE_DECLTYPES)
        with con:
            cur = con.cursor()    
            cur.execute("CREATE TABLE temperature(Id integer primary key, sensorName text, regDate timestamp, value float, reported integer)")
            con.commit()   
    
    def scheduleJob(self, propertyName, jobFunction):
        for key in self.schedule:
            val = self.schedule[key]
            if val == None:
                return
            paramKey = key[:len(propertyName)]
            if paramKey == propertyName:
                scheduleType = key[len(propertyName)+1:]
                if scheduleType == 'at':
                    schedule2.every().day.at(val).do(jobFunction)
                    return
                elif scheduleType == 'period.seconds':
                    schedule2.every(float(val)).seconds.do(jobFunction)
                    return
                elif scheduleType == 'period.minutes':
                    schedule2.every(float(val)).minutes.do(jobFunction)
                    return
                elif scheduleType == 'period.hours':
                    schedule2.every(float(val)).hours.do(jobFunction)
                    return
                            
    def doPoll(self):
        time.sleep(10)
        self.checkCorrectStop()
        self.scheduleJob('checkTemperatureTrigger', self.checkTemperatureTrigger)
        self.scheduleJob('updatePowerFile', self.updatePowerFile)
        self.scheduleJob('updateTemperatureHistory', self.updateTemperatureHistory)
        self.scheduleJob('reportTemperatureHistory', self.reportTemperatureHistory)
        
        while not self.toBeStopped:
            try:
                schedule2.run_pending()
            except:
                util.logger.error("unable to execute job %s" , traceback.format_exc())
                print "unable to execute job %s" % traceback.format_exc()
            time.sleep(1)
        self.stopped = True    
                
    def stop(self):
        self.toBeStopped = True
        while not self.stopped:
            time.sleep(1)
        util.deleteTempFile(Manager.powerFileName)    
        
            
            
    def __init__(self, params):
        '''
        Constructor
        '''
        jabberDevice = 'jabber'
        sendTo = params['jabber.sendTo'] 
        if 'jabber.deviceName' in params:
            jabberDevice = params['jabber.deviceName']
        config = util.readConfig('config.cfg')
        port = config['port']    
        self.jabberUrl = "http://localhost:%s/write/%s?to=%s" %(port, jabberDevice,sendTo)
        self.httpPort = port
        self.phoneNumber = params['phone']
        self.tmins = dict()
        for sensorName in Manager.sensorsNames:
            self.tmins[sensorName] = float(params["min%s" % sensorName])
        
        self.timeFormat = "%d/%m/%y %H:%M"
        self.startTime = time.time()
        self.stopped = False
        self.toBeStopped = False
        self.schedule = dict()
        for key in params:
            if key.startswith('schedule'):
                self.schedule[key[len('schedule')+1:]] = params[key]
        
        jobRunner = threading.Thread(target=self.doPoll)
        jobRunner.start()
        
        
    
           
