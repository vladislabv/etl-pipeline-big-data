import os
import requests
#import pymongo
from dotenv import load_dotenv
from datetime import datetime, timezone
from api import check_api_is_up, get_gateways, get_tags, get_measurements
from update import updateInsert, getLastPageNumber, deleteMeasurements, checkLastTag


load_dotenv()  # take environment variables from .env.

HOST = os.getenv('API_HOST')
HEADERS = {'accept': 'application/json'}

# open session
with requests.Session() as s:
    # delete all previously collected data from the database, i.e. new start - new life :)
    # deleteMeasurements()
    
    # set request headers
    s.headers.update(HEADERS)
    print(f'Checking if API is up at {HOST}')
    
    if check_api_is_up(s):
        print('API is up')
        print('Getting gateways')
    
        #Endlosschleife fuer die abfrage der Daten
        while True:
            
            #run through all gateways as stream
            for gateway in get_gateways(s):
                
                #change dataframe structure for new mongodb structure
                gateway['ip4'] = gateway.pop('ip_address')
                gateway['net_segment'] = gateway.pop('network_segment')
                gateway['_id'] = gateway.pop('id')
                #delte Nanoseconds for timestamp cast
                gateway['last_contact'] = datetime.strptime(gateway['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                gateway['tags_assigned'] = []

                #run through all tags for the selected gateway
                for tag in get_tags(s, gateway['_id']):
                    #delete nano-seconds for timestamp cast
                    tag['last_contact'] = datetime.strptime(tag['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                    tag.pop('sensors')
                    #set the inserttimestamp for tag history
                    tag['inserttimestamp'] = datetime.now(timezone.utc)

                    #add the tag address to the added tag array for the gatewys
                    if not tag['address'] in gateway['tags_assigned']:
                        gateway['tags_assigned'].append(tag['address'])
                    
                    #get the last added tag and check if there is a change in config or settings
                    if checkLastTag(tag):
                        #add the last tag if there is a change
                        updateInsert('tags', tag)

                    #run through all measurements
                    for measurement in get_measurements(s, tag['address'], getLastPageNumber(tag['address'])):
                        #delte nano-seconds and add the sturucture fields
                        measurement['recorded_time'] = datetime.strptime(measurement['recorded_time'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                        measurement['gateway_id'] = gateway['_id']
                        measurement['tag_address'] = tag['address']

                        #insert the measurement with the last settings
                        updateInsert('measures', measurement)

                #insert the gateway with all added tags
                updateInsert('gateways', gateway)
    else:    
        print('API is not up. Program will be closed')
        