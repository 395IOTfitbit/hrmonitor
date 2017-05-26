"""
Get Data from fitbit
"""

import json
import time
import urllib
import urllib2

codes = json.loads(open('codes.json').read())
access_code = codes['access_token']
user_id = codes['user_id']
client_id = "2288W8"

data = {}

headers = {
    "Authorization": "Bearer "+access_code
}

#req = urllib2.Request("https://api.fitbit.com/1/user/"+user_id+"/sleep/date/2017-04-21.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/-/heart/date/2017-04-20.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/"+user_id+"/activities/heart/date/today/1d.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/-/sleep/minutesAsleep/date/2017-04-11/7d.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/-/activities/steps/date/today/1m.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/-/activities.json", urllib.urlencode(data), headers)

#req = urllib2.Request("https://api.fitbit.com/1/user/"+user_id+"/activities/heart/date/today/1m.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/"+user_id+"/activities/heart/date/today/1d/1sec/time/00:00/00:01.json", urllib.urlencode(data), headers)
#req = urllib2.Request("https://api.fitbit.com/1/user/5MH8SH/profile.json", urllib.urlencode(data), headers)
"""for i in range(1, 10):
    req = urllib2.Request("https://api.fitbit.com/1/user/5MH8SH/heart/date/2017-05-0"+str(i)+".json", urllib.urlencode(data), headers)
    try:
        response = urllib2.urlopen(req)
        print(response.read())
    except urllib2.HTTPError:
        pass
    time.sleep(1)"""

#5MH8SH

#req = urllib2.Request("https://api.fitbit.com/1/user/5MH8SH/heart/data/2017-04-20.json", headers)
#response = urllib2.urlopen(req)
#print(response.read())

##print(urllib2.urlopen("https://api.fitbit.com/1/user/"+user_id+"/activities/heart/date/today/1d.json").read())

"""
Simluation stuff
"""
req = urllib2.Request("http://localhost:49494/?"+urllib.urlencode({"PVC": False, "AFVF": False, "NOHR": False}))
response = urllib2.urlopen(req)
print(response.read())
