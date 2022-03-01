
from phue import Bridge
from pprint import pprint
import pymongo

b = Bridge('192.168.1.214')

# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
b.connect()

# Get the bridge state (This returns the full dictionary that you can explore)
b.get_api()

lights = b.lights
with open("/home/pi/.mongo_uri.txt") as f:
    uri = f.readline().strip()
    mongoclient = pymongo.MongoClient(uri)

# Print light names
lightinfo = []
for l in lights:
    if l.on:
        rec = { 'on':l.on, 'n': 'Hue bulb', 'name': l.name, 'brightness': l.brightness, "watts" : (9 * l.brightness) / 254}
        lightinfo.append(rec)

if len(lightinfo)>0:
        #Append this to an array in the latest electicity reading
        collection = mongoclient.energy.meter
        query = {"type":"electric"}
        sort =[('date', -1)]
        update = { "$push" : { "devices" : { "$each" : lightinfo} }}
        collection.find_one_and_update(query,update,sort=sort)







