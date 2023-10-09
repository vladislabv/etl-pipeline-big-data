import os
import requests
import pymongo
from dotenv import load_dotenv
from datetime import datetime, timezone
from api import check_api_is_up, get_gateways, get_tags, get_measurements, get_config
from update import updateInsert

def main():
    # open session
    with (requests.Session() as s,
        pymongo.MongoClient(MONGO_URI) as client):
        # set headers
        db = client['MongoDB-Database']
        s.headers.update(HEADERS)
        print(f'Checking if API is up at {HOST}')
        if check_api_is_up(s):
            print('API is up')
        
            for gateway in get_gateways(s):

                gatewayconfig = get_config(s, gateway["id"])
                
                gateway['ip4'] = gateway.pop('ip_address')
                gateway['net_segment'] = gateway.pop('network_segment')
                gateway['_id'] = gateway.pop('id')
                gateway['last_contact'] = datetime.fromisoformat(gateway['last_contact'])
                #gateway['last_contact'] = datetime.strptime(gateway['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                
                gateway['config'] = gatewayconfig
                gateway['tags_assigned'] = []

                for tag in get_tags(s, gateway['_id']):
                    numbertags += 1
                    print(f'Tag: {tag["address"]}\n')

                    tag['_id'] = tag.pop('address')
                    tag['last_contact'] = datetime.strptime(tag['last_contact'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
                    tag.pop('sensors')

                    tagconfig = get_config(s, gateway["_id"], tag['_id'])
                    print(f'Config for tag: {tagconfig}\n')

                    tag['config'] = tagconfig
                
                    gateway['tags_assigned'].append(tag['_id'])
                    
                    updateInsert('tags', tag)

                    print('Getting measurements')

                    for measurement in get_measurements(s, tag['_id']):
                        measurement['tag_id'] = tag['_id']
                
                updateInsert('gateways', gateway)
                
        else:    
            print('API is not up. Program will be closed')


if __name__ == '__main__':

    load_dotenv(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env'
        )
    )  # take environment variables from .env.

    HOST = os.getenv('API_HOST')
    HEADERS = {'accept': 'application/json'}
    MONGO_URI = os.getenv('MONGO_URI')

    main()

