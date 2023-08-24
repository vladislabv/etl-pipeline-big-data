import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

API = os.getenv('API_HOST') + os.getenv('API_BASE_URL')

# get data from API
def check_api_is_up(session):
    try:
        r = session.get(f'{API}/ping')
        if r.status_code == 200 and r.json()['message'] == 'pong':
            return True
        else:
            return False
    except:
        return False


def get_gateways(session):
    r = session.get(f'{API}/structure/gateway/list')
    yield from r.json()['gateways']


def get_tags(session, gateway_id):
    r = session.get(f'{API}/structure/tag/list/{gateway_id}')
    yield from r.json()


def stop_iteration(elem, stop_at):
    return datetime.fromisoformat(elem['recorded_time']) < stop_at.replace(tzinfo=timezone.utc)


# Caution for really long measurements running this function will take a long time
# by default only measures from 12 hours ago are returned
def get_measurements(session, tag_ip6, stop_at=(datetime.now()-timedelta(hours=12)), start_page=1, paginate=True):
    r = session.get(f'{API}/acc-data/get/{tag_ip6}/{start_page}')
    res = r.json()
    if not 'measurements' in res.keys() or not int(res['size']):
        print(f'No measurements for {tag_ip6}')
        return
    # yield found measurements
    for measurement in res['measurements']:
        if measurement:
            yield measurement

    if paginate:
        # iterate over the measurements
        while True:
            start_page += 1
            r = session.get(f'{API}/acc-data/get/{tag_ip6}/{start_page}')
            res = r.json()
            for measurement in res['measurements']:
                if measurement and not stop_iteration(measurement, stop_at):
                    yield measurement


def get_configs(session: requests.Session, gateway_ids: list, obj: str = "gateway", tag_ip6s = None):
    if obj not in ["gateway", "tag"]:
        raise ValueError("obj must be either 'gateway' or 'tag'")
    
    if not isinstance(gateway_ids, list):
        raise ValueError("gateway_ids must be a list")
    
    if obj == "tag":
        if not isinstance(tag_ip6s, list):
            raise ValueError("tag_ip6s must be a list")
        if not len(gateway_ids) == len(tag_ip6s):
            raise ValueError("Length of gateway_ids and tag_ip6s must be equal")     

        for id, ip6 in zip(gateway_ids, tag_ip6s):
            r = session.get(f'{API}/config/get/{id}/{ip6}')
            yield r.json()['config']
    else:
        for id in gateway_ids:
            r = session.get(f'{API}/config/get/{id}')
            yield r.json()['config']