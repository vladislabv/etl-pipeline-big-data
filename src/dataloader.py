import os
import requests
#import pymongo
from dotenv import load_dotenv

from api import check_api_is_up, get_gateways, get_tags, get_measurements, get_configs, get_configssing

load_dotenv()  # take environment variables from .env.

HOST = os.getenv('API_HOST')
HEADERS = {'accept': 'application/json'}

# open session
with requests.Session() as s:
    # set headers
    numbermeasurements = 0
    s.headers.update(HEADERS)
    print(f'Checking if API is up at {HOST}')
    if check_api_is_up(s):
        print('API is up')
        print('Getting gateways')
    
        for gateway in get_gateways(s):
            print(f'Gateway: {gateway["id"]}\n')
            print('Getting tags')

            gatewayconfig = get_configssing(s, gateway["id"])
            print(f'Config for gateway: {gatewayconfig}\n')

            for tag in get_tags(s, gateway['id']):
                print(f'Tag: {tag["address"]}\n')
                
                tagconfig = get_configssing(s, gateway["id"], tag['address'])
                print(f'Config for tag: {tagconfig}\n')

                print('Getting measurements')
                
                for measurement in get_measurements(s, tag['address']):
                    numbermeasurements += 1
                    print(f'Measurement: {measurement}\n')
                    
        print("Everything loaded with " + str(numbermeasurements) + " measurements")
    else:    
        print('API is not up. Program will be closed')



# establish database connection
#client = pymongo.MongoClient("mongodb://localhost:27017/")
#db = client["test"]

