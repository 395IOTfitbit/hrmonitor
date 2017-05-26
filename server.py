"""
A simple server that serves an HTML file
"""

#Global
import base64
import BaseHTTPServer
import json
import os
import time
import threading
import SimpleHTTPServer
import SocketServer
import ssl
import subprocess
import urllib
import urllib2

#Local

CODES_PATH = 'codes.json'

CLIENT_ID = "2288W8"

CLIENT_SECRET = "773dd7eea1c1660598fb3fdaeccd0170"

FB_URL = "https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=2288W8&redirect_uri=https%3A%2F%2Fhoundstooth.cs.northwestern.edu%3A49494%2Ffitbit_auth&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight"

def update_hr_file(new_d, path="./user_hr.json"):
    try:
        old_d = json.loads(open(path).read())
        for i in range(1, 10):
            old_d[i] = old_d[i-1]
        old_d[0] = new_d
    except IOError:
        old_d = {}
        for i in range(10):
            old_d[i] = {}
        old_d[0] = new_d
    open(path, 'w').write(json.dumps(old_d))

def monitor_loop():
    """This function should be started in a separate thread.  It will query the simulated server every minute
    and update a local JSON file.  The JSON file stores the last 10 minutes of data"""
    while True:
        req = urllib2.Request("http://localhost:49449/?"+urllib.urlencode({"PVC": False, "AFVF": False, "NOHR": False}))
        response = urllib2.urlopen(req)
        new_d = json.loads(response.read())
        update_hr_file(new_d)


        time.sleep(60)

def save_code(key, code):
    jd = json.loads(open(CODES_PATH).read())
    jd[key] = code
    open(CODES_PATH, 'w').write(json.dumps(jd))

def get_code(key):
    jd = json.loads(open(CODES_PATH).read())
    return jd[key]

class CustomServer(BaseHTTPServer.BaseHTTPRequestHandler):        
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        print(self.path)
    
        if self.path == '/index' or self.path == '/':
            self.wfile.write(open('index.html').read())
        elif "fitbit_auth" in self.path:
            if "code" in self.path:
                authorization_code = self.path.split('=')[1]
                save_code('authorization_code', authorization_code)
                reqstr = base64.b64encode(CLIENT_ID+":"+CLIENT_SECRET)
                data = {
                    "code": authorization_code,
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "redirect_uri": "https://houndstooth.cs.northwestern.edu:49494/fitbit_auth"
                }
                headers = {"Authorization": "Basic "+reqstr, "Content-type": "application/x-www-form-urlencoded"}
                req = urllib2.Request("https://api.fitbit.com/oauth2/token", urllib.urlencode(data), headers)
                resp = urllib2.urlopen(req)
                resp_jd = json.loads(resp.read())
                save_code("access_token", resp_jd['access_token'])
                save_code("user_id", resp_jd["user_id"])
                save_code("refresh_token", resp_jd["refresh_token"])
                print(resp.read())
                monitor = threading.Thread(target=monitor_loop)
                monitor.start()
        else:
            self.wfile.write(open(os.getcwd()+self.path).read())
        return       

def server():
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", 49494), Handler)
    httpd.serve_forever()

def ssl_server():
    """https://anvileight.uk/blog/2016/03/20/simple-http-server-with-python/"""
    #httpd = BaseHTTPServer.HTTPServer(("", 49494),
    #    SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd = BaseHTTPServer.HTTPServer(("", 49494),
        CustomServer)
    httpd.socket = ssl.wrap_socket(httpd.socket,
        keyfile="key.pem",
        certfile='cert.pem', server_side=True)
    httpd.serve_forever()    

if __name__ == "__main__":
    #server()
    ssl_server()
