"""
This code generates simulated heart rate time-series data because Fitbit sucks.

Data structure:

For the time range specified, Fitbit sends back a list of objects
    
    {"dateTime": "##:##:##", "value": "#"}

The real Fitbit API allows for customization of the response in terms
of range and interval of timeseries data.  This simplified version, when
queried, will always generate 60 seconds of heart rate data incremented every
second, so 60 of the above objects.

Simulating heart conditions:
    --PVC: A missed heartbeat. Simulated by one of the above data objects
        containing a heart rate value that is < 10% below the moving average.

    --AF/VF: Simulated by heart rate between 150-300 for > 30s

    --No HR: Simluated by heart rate of 0 for > 30s

    --Regular heartbeat - some value within +-10% of chosen resting value

Server

The server accepts an HTTP Request with the following JSON object:
    
    {
        "PVC": true/false
        "AFVF": true/false
        "NOHR": true/false
    }

and generates data based on those parameters
"""

#Global
import BaseHTTPServer
import json
import math
import random
import urlparse

#Local

class HRSim:
    """Implements generation functions for heart rate data and various disorders
    as described above"""
    def __init__(self, N, resting):
        self.ma = 0.0  #moving average
        self.ns = 0  #num samples  (stop updating once == N) (use while < N)
        self.N = N   #num samples to use in moving average
        self.resting = resting  #resting heart rate

    def build_hr_data(self, conf_d):
        """Takes the config from the HTTP request (as described above) and generates
        simulated heart rate data.  Updates number of samples, moving average, and returns
        the generated data JSON"""
        hr_l = []  #list of objects as described above
        second = 0
        while len(hr_l) < 60:
            if conf_d["PVC"] == "True":
                hr_l += self.build_pvc_sample(second) #should be a list of 1 sample
                conf_d["PVC"] = "False"
                second += 1
            elif conf_d["AFVF"] == "True":
                hr_l += self.build_afvf_samples(second) #should be a list of 40 samples
                conf_d["AFVF"] = "False"
                second += 30
            elif conf_d["NOHR"] == "True":
                hr_l += self.build_nohr_samples(second) #should be a list of 40 samples
                conf_d["NOHR"] = "False"
                second += 40
            else:
                hr_l += self.build_regular_sample(second)  #should be a list of 1 sample
                second += 1
        self.update_ma(hr_l)
        if self.ns < self.N:
            self.ns += len(hr_l)
        return json.dumps({"data": hr_l})

    def build_pvc_sample(self, second):
        """This sample should be > 10% below the current moving average"""
        sample_d = {"dateTime": "00:00:"+self.second2str(second)}
        #if self.ma != 0:
        #    perc_10_ma = self.ma * 0.1
        #    upper_bound = self.ma - perc_10_ma
        #else:
        perc_10_ma = self.resting * 0.1
        upper_bound = self.resting - perc_10_ma
        print("moving average: "+str(self.ma))
        print("10 percent of moving average: "+str(perc_10_ma))
        print("upper bound: "+str(upper_bound))
        sample_d["value"] = str(random.randint(math.floor(upper_bound-15), math.floor(upper_bound)))
        return [sample_d]

    def build_afvf_samples(self, second):
        """Returns 40 samples between 190 and 210"""
        sample_l = []
        for i in range(40):
            sample_d = {"dateTime": "00:00:"+self.second2str(second)}
            sample_d["value"] = str(random.randint(190, 210))
            sample_l.append(sample_d)
            second += 1
        return sample_l

    def build_nohr_samples(self, second):
        """Returns 40 samples with 0 hr"""
        sample_l = []
        for i in range(40):
            sample_d = {"dateTime": "00:00:"+self.second2str(second)}
            sample_d["value"] = "0"
            sample_l.append(sample_d)
            second += 1
        return sample_l

    def build_regular_sample(self, second):
        """Returns 1 sample within +-10% of resting"""
        sample_d = {"dateTime": "00:00:"+self.second2str(second)}
        #if self.ma != 0:
        #    perc_10_ma = self.ma*.1
        #    sample_d["value"] = str(random.randint(math.floor(self.ma-perc_10_ma), math.floor(self.ma+perc_10_ma)))
        #else:
        perc_10_ma = self.resting * 0.1
        sample_d["value"] = str(random.randint(self.resting-perc_10_ma, self.resting+perc_10_ma))
        return [sample_d]
    
    def update_ma(self, hr_l):
        if self.ma == 0.0:
            self.ma = sum([float(sample["value"]) for sample in hr_l]) / float(len(hr_l))
        else:
            for sample in hr_l:
                self.ma -= self.ma/self.N
                self.ma += float(sample["value"]) / self.N
        print("updated moving average: "+str(self.ma))
        
    def second2str(self, second):
        """Converts the seconds integer into a double digit string"""
        if second < 10:
            return "0"+str(second)
        return str(second)

class FitbitSimServer:
    def __init__(self, hrsim):
        FitbitSimServerHandler.hrsim = hrsim
        server = BaseHTTPServer.HTTPServer(("", 49449), FitbitSimServerHandler)
        server.serve_forever()

class FitbitSimServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    hrsim = None
    def do_GET(self):
        print(hrsim)
        req = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(req.query)
        hr_config = {}
        for key in params:
            hr_config[key] = params[key][0]
        hr_data = self.hrsim.build_hr_data(hr_config)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(hr_data)

if __name__ == "__main__":
    print("fitbit heartrate timeseries simulated server")
    #httpd = BaseHTTPServer.HTTPServer(("", 49494), FitbitSimServer)
    #httpd.serve_forever()

    #hrsim = HRSim(100, 60)
    #conf_d = {
    #    "PVC": "False",
    #    "AFVF": "False",
    #    "NOHR": "True"
    #}
    #print(hrsim.build_hr_data(conf_d))

    hrsim = HRSim(100, 60)
    FitbitSimServer(hrsim)
