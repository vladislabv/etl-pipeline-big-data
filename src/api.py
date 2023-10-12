import os
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
   #Drop nanoseconds since they are not supported by mongoDB
   return datetime.strptime(elem['recorded_time'][:-4], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc) < stop_at.replace(tzinfo=timezone.utc)


# Caution for really long measurements running this function will take a long time
# by default only measures from 12 hours ago are returned
def get_measurements(session, tag_ip6, start_page=1, stop_at=(datetime.now()-timedelta(hours=12)), paginate=True):    
    r = session.get(f'{API}/acc-data/get/{tag_ip6}/{start_page}')
    if r.status_code == 200:
        res = r.json()
        if not 'measurements' in res.keys() or not int(res['size']):
            print(f'No measurements for {tag_ip6}')
            return
        # yield found measurements
        for measurement in res['measurements']:
            if measurement and (res['size'] == 10):
                measurement['page'] =  res['page']
                yield measurement

        if paginate:
            # iterate over the measurements
            nextTag = False
            measuredPages = 0
            while not nextTag:
                measuredPages += 1
                start_page += 1
                r = session.get(f'{API}/acc-data/get/{tag_ip6}/{start_page}')
                if r.status_code == 200:
                    res = r.json()
                    if ((res['page'] < res['next_page']) and (res['size'] == 10) and measuredPages < 20):
                        for measurement in res['measurements']:
                            if measurement and not stop_iteration(measurement, stop_at):
                                measurement['page'] = res['page']
                                yield measurement
                    else:
                        nextTag = True
