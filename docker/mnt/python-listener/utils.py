import json
import logging
import datetime as dt

import aiofiles

logger = logging.getLogger(__name__)

def convert_go_timestamp(tmp: str) -> dt.datetime:
    return dt.datetime.strptime(
        tmp[:-4], # cut nanoseconds
        "%Y-%m-%dT%H:%M:%S.%f" # format with microseconds only
    ).replace(
        tzinfo=dt.timezone.utc # set timezone to be utc
    )

async def read_json_file(filename):
    if not filename.split('.')[-1] == "json":
        return
    async with aiofiles.open(filename, mode="r") as file:
        contents = json.loads(await file.read())
    return contents