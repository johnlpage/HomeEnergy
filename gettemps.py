from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from pprint import pprint
import time
import pymongo
import datetime

TEMPERATURE_SERVICE_UUID = "e95d6100-251d-470a-a062-fa1922dfa9a8";
TEMPERATURE_CHARACTERISTIC_UUID = "e95d9250-251d-470a-a062-fa1922dfa9a8";

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
       pass

with open('/home/pi/.mongo_uri.txt') as f:
    uri = f.readline().strip()
    mongoclient = pymongo.MongoClient(uri)


map = { "c7:03:41:4f:6b:61": "office","d4:7d:86:27:03:d2": "upstairshall", "d4:26:d7:2d:dc:a7":"utility", "d1:a0:81:06:f5:23" : "GamesRoom","dd:ec:c8:b2:0b:64" : "Hallway", "d0:27:86:a2:95:e1" :"LivingRoom"}

def send_temp_to_atlas(dev,temp):
    mongoclient.energy.roomtemps.insert_one({"date": datetime.datetime.now(), "location": map.get(dev,"unknown"), "temp": temp})


#BT comms can fail randomly
def read_temp(dev):
    for a in range(5):
        try:
            microbit = Peripheral(dev)
            print("Connected")
            print("Getting Service Handle")
            tempService = microbit.getServiceByUUID(TEMPERATURE_SERVICE_UUID)
            print("Getting Characteristic Handle")
            characteristics = tempService.getCharacteristics(forUUID=TEMPERATURE_CHARACTERISTIC_UUID)
            print("Getting  value")
            temp = int.from_bytes(characteristics[0].read(),"big")
            print(F"Device: {dev.addr} Temp: {temp}")
            send_temp_to_atlas(dev.addr,temp)
            return;
        except Exception as e:
            print(e)

#Scan for any and all Bluetooth devices for 10 seconds.
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)

time.sleep(2)
for dev in devices:
    #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
     
        if value.startswith("BBC micro:bit"):
            print(f"Microbit found {value}")
            read_temp(dev)

