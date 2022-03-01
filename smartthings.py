import aiohttp
import pysmartthings
import pymongo
import asyncio
from pprint import pprint

with open("/home/pi/.smartthing_token") as f:
        token = f.readline().strip()

interesting_attributes = ['n','powerConsumption','switch',]


async def log_devices():
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, token)
        devices = await api.devices()
        #print(len(devices))
        deviceinfo = []
        for device in devices:
            try:
                name = device.label
                #Dont record my mobile phone
                if "Tully" not in name:
                    await device.status.refresh()
                    turned_on = device.status.switch

                    record = { "on" : turned_on, "name":name}
                    for a in interesting_attributes:
                        v = device.status.values.get(a,None)
                        if v != None:
                            record[a]=v

                    #Let's not waste space on things that are off
                    if turned_on:
                        deviceinfo.append(record)
               
            except Exception as e:
                #Fridge returns an auth error?
                print(e)
    return deviceinfo


def main():
    with open("/home/pi/.mongo_uri.txt") as f:
        uri = f.readline().strip()
        mongoclient = pymongo.MongoClient(uri)

    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(log_devices())
    loop.close()
    pprint(devices)
    if len(devices)>0:
        #Append this to an array in the latest electicity reading
        collection = mongoclient.energy.meter
        query = {"type":"electric"}
        sort =[('date', -1)]
        update = { "$push" : { "devices" : { "$each" : devices} }}
        collection.find_one_and_update(query,update,sort=sort)
       


if __name__ == "__main__":
    main()
