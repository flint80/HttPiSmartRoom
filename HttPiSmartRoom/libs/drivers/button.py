'''
Created on Oct 21, 2015

@author: avramenko
'''
import RPi.GPIO as GPIO
from utils import util
import urlparse
import httplib
import traceback
import threading
import time

class Button():
    '''
    check for button push
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        self.pin = int(params["pin"])
        self.url=params["url"]
        self.stopped = False
        self.old_state = 0
        self.new_state_count = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        thread = threading.Thread(target=self.poll_button)
        thread.setDaemon(True)
        thread.start()

        #GPIO.add_event_detect(self.pin, GPIO.RISING)

        def button_callback(arg):
            self.executeCommand()

        #GPIO.add_event_callback(self.pin, button_callback)

    def executeCommand(self):
        util.logger.debug("button %s pressed" % (self.pin))
        conn = None
        try:
            parseResult = urlparse.urlparse(self.url)
            server = parseResult.netloc
            conn = httplib.HTTPConnection(server)
            path = "%s?%s" % (parseResult.path, parseResult.query)
            conn.request('POST', path, "")
            result = conn.getresponse()
            util.logger.debug("result.status = %s, result.reason = %s" % (result.status, result.reason))
        except:
            util.logger.error("unable to send message: %s" , traceback.format_exc())
        finally:
            if conn:
                conn.close()

    def poll_button(self):
        while not self.stopped:
            time.sleep(0.2)
            i = GPIO.input(self.pin)
            if i == 0:
                self.old_state=0
                self.new_state_count=0;
            elif self.old_state==0:
                self.new_state_count = self.new_state_count+1;
                if self.new_state_count > 4:
                    self.old_state=i;
                    self.executeCommand()

    def stop(self):
        self.stopped = True
        GPIO.cleanup()
            

