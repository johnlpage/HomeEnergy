from PyP100 import PyP110
import json
from pprint import pprint
import pymongo

with open("/home/pi/.mongo_uri.txt") as f:
    uri = f.readline().strip()
    mongoclient = pymongo.MongoClient(uri)

tapoplugs = { "dryer": "192.168.1.54","malawi tank":"192.168.1.99","television":"192.168.1.55","guppy tank":"192.168.1.31"}

with open("/home/pi/.tapopass") as f:
        password = f.readline().strip()
devices = []

for plug in tapoplugs:
    ip = tapoplugs[plug]
    try:
        p110 = PyP110.P110(ip, "johnlpage@gmail.com", password) #Creating a P110 plug object

        p110.handshake() #Creates the cookies required for further methods
        p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

        #PyP110 has all PyP100 functions and additionally allows to query energy usage infos
        data = p110.getEnergyUsage() #Returns dict with all the energy usage

        print(json.dumps(data))
        if data["result"]["current_power"] > 1500:
            #It's Milliwatts
            rec = {"name": plug, "n": "plug", "on":True, "watts": (data["result"]["current_power"])/1000 }
            devices.append(rec)

    except Exception as e:
        print(e)

if len(devices)>0:
        #Append this to an array in the latest electicity reading
        collection = mongoclient.energy.meter
        query = {"type":"electric"}
        sort =[('date', -1)]
        update = { "$push" : { "devices" : { "$each" : devices} }}
        collection.find_one_and_update(query,update,sort=sort)
