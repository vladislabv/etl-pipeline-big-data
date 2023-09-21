import os
import requests
#import pymongo
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from api import check_api_is_up, get_gateways, get_tags, get_measurements, get_configs, get_configssing
from update import updateInsert, closeclient


load_dotenv()  # take environment variables from .env.

HOST = os.getenv('API_HOST')
HEADERS = {'accept': 'application/json'}

# open session
with requests.Session() as s:
    # set headers
    numbermeasurements = 0
    numbergateways = 0
    numbertags = 0

    s.headers.update(HEADERS)
    print(f'Checking if API is up at {HOST}')
    if check_api_is_up(s):
        print('API is up')
        print('Getting gateways')
    
        for gateway in get_gateways(s):
            numbergateways += 1
            print(f'Gateway: {gateway["id"]}\n')
            print('Getting tags')

            gatewayconfig = get_configssing(s, gateway["id"])
            
            gateway['ip4'] = gateway.pop('ip_address')
            gateway['net_segment'] = gateway.pop('network_segment')
            gateway['_id'] = gateway.pop('id')
            gateway['last_contact'] = datetime.strptime(gateway['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)

            gateway['config'] = gatewayconfig
            gateway['tags_assigned'] = []

            print(f'Config for gateway: {gatewayconfig}\n')

            for tag in get_tags(s, gateway['_id']):
                numbertags += 1
                print(f'Tag: {tag["address"]}\n')

                tag['_id'] = tag.pop('address')
                tag['last_contact'] = datetime.strptime(tag['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                tag.pop('sensors')

                tagconfig = get_configssing(s, gateway["_id"], tag['_id'])
                print(f'Config for tag: {tagconfig}\n')

                tag['config'] = tagconfig
            
                gateway['tags_assigned'].append(tag['_id'])
                
                updateInsert('tags', tag)

                print('Getting measurements')

                for measurement in get_measurements(s, tag['_id']):
                    numbermeasurements += 1
                    measurement['recorded_time'] = datetime.strptime(measurement['recorded_time'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                    measurement['tag_id'] = tag['_id']
                    updateInsert('measures', measurement)
                    print(f'Measurement: {measurement}\n')
            


            updateInsert('gateways', gateway)

        closeclient            
        print("Everything loaded with " + str(numbermeasurements) + " measurements, " + str(numbertags) + " tags und  " + str(numbergateways) + " gateways ")
    else:    
        print('API is not up. Program will be closed')



# establish database connection
#client = pymongo.MongoClient("mongodb://localhost:27017/")
#db = client["test"]

