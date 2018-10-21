'''
Created on Oct 20, 2015

@author: avramenko
'''
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
import threading
from utils import util
import traceback

httpConfig = None
server = None

class HttpServerConfiguration():
    
    mapping = {}
    
    port = 8080
    
    pass

class GetHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Log an arbitrary message.

        This is used by all other logging functions.  Override
        it if you have specific logging wishes.

        The first argument, FORMAT, is a format string for the
        message to be logged.  If the format string contains
        any % escapes requiring parameters, they should be
        specified as subsequent arguments (it's just like
        printf!).

        The client ip address and current date/time are prefixed to every
        message.

        """

        util.logger.debug("%s - - [%s] %s\n" %
                         (self.client_address[0],
                          self.log_date_time_string(),
                          format%args))
    def killServer(self):
        assassin = threading.Thread(target=server.shutdown)
        assassin.daemon = True
        assassin.start()    
        
    def do_GET(self):
        global httpConfig
        parsed_path = urlparse.urlparse(self.path)
        util.logger.debug("handling GET request, path = %s, query = %s" % (parsed_path.path, parsed_path.query))
        if parsed_path.path == '/stop':
            util.logger.debug("stopping server")
            for deviceName in httpConfig.mapping:
                device = httpConfig.mapping[deviceName]
                try:
                    device.stop()
                except AttributeError: 
                    pass
            assassin = threading.Thread(target=server.shutdown)
            assassin.daemon = True
            assassin.start()
            return
        if parsed_path.path == '/check':
            util.logger.debug("checking server state")
            try:
                self.send_response(200)
            except:
                pass    
            return
        if parsed_path.path[0:5] == '/read':
            try:
                deviceName = parsed_path.path[6:].strip()
                params = urlparse.parse_qs(parsed_path.query)
                device = httpConfig.mapping[deviceName]
                util.logger.debug("reading device %s state" % deviceName)
                result = device.getValue(params)
                util.logger.debug("result is %s" % result)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result)
                return
            except:
                util.logger.error("unable to get value for query %s, \n details: %s" % (self.path, traceback.format_exc()))
                try:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("error")
                    return
                except:
                    util.logger.error("unable to send response, \n details: %s" % (traceback.format_exc()))
                    return
        util.logger.warn("unknown request type %s" % self.path)
        self.send_response(200)
        self.end_headers()
        return
    
    def do_POST(self):
        global httpConfig
        parsed_path = urlparse.urlparse(self.path)
        util.logger.debug("handling POST request, path = %s, query = %s" % (parsed_path.path, parsed_path.query))
        if parsed_path.path[0:6] == '/write':
            try:
                deviceName = parsed_path.path[7:].strip()
                params = urlparse.parse_qs(parsed_path.query)
                for key in params:
                    value = params[key]
                    if len(value) == 1:
                        params[key] = value[0]
                device = httpConfig.mapping[deviceName]
                content_len = int(self.headers.getheader('content-length', 0))
                body = self.rfile.read(content_len)
                util.logger.debug("writing to device %s" % deviceName)
                result = device.setValue(params, body)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result)
                return
            except:
                util.logger.error("unable to set value value for query %s, \n details: %s" % (self.path, traceback.format_exc()))
                self.send_response(400)
                self.end_headers()
                self.wfile.write("error")
                return    
        util.logger.warn("unknown request type %s" % self.path)
        self.send_response(200)
        self.end_headers()
        return

    
    
class HttpServer():
    
    '''
    HttpServer routes http requests to handlers
    '''
    
    def __init__(self, conf):
        '''
        httpConfig: instance of HttpServerConfiguration
        '''
        global httpConfig, server
        httpConfig = conf
        server = HTTPServer(('', httpConfig.port), GetHandler)
        print "server started"
        server.serve_forever()
        
        