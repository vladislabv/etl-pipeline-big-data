import logging
from utils import read_json_file

logger = logging.getLogger(__name__)

async def ping_client(client):
    async with await client.start_session() as s:
        try:
            pong = await client.list_database_names(session=s)
        except Exception as e:
            raise e
    assert pong is not None and len(pong) > 0
    return 'pong'


async def setup_database(db):
    async with await db.start_session() as s:
        check = await db.list_database_names(session=s)
        assert check is not None and len(check) > 0
        try:
            if "gateways" not in check:
                v = read_json_file("mongodb/validators/collection_schema_gateways.json")
                _ = await db.create_collection("gateways", validator=v)
            if "tags" not in check:
                v = read_json_file("mongodb/validators/collection_schema_tags.json")
                _ = await db.create_collection("tags", validator=v)
                _ = await db.tags.create_index({"address": 1}, name="address_search", unique=False)
            if "measures" not in check:
                v = read_json_file("mongodb/validators/collection_schema_measures.json")
                _ = await db.create_collection("measures", validator=v, timeseries={"timeField": "recorded_time", "granularity": "seconds"})
        except Exception as e:
            print(e)
        # check if collections exists
    return 'All collections are setup or already existed'


async def do_insert_on_change(conn, d, ref_field, avoid_keys, s):
    old_d = await conn.find_one({ref_field: d[ref_field]}, sort=[("_id", -1)], session=s)
    if not old_d:
        await do_insert(conn, document=d, session=s)
        return
    d_tmp = {i: d.pop(i, '') for i in avoid_keys}
    _ = {j: old_d.pop(j, '') for j in avoid_keys + ['_id']}
    # check if subset of dicts is equal, meaning the doc not changed (except specific fields)
    if old_d != d:
        d |= d_tmp
        await do_insert(conn, document=d, session=s)
    return


async def do_insert(conn, document, session):
    try:
        result = await conn.insert_one(document, session=session)
        logger.info('Inserted new object with id: %s' % repr(result.inserted_id))
    except Exception as e:
        print(e)
        logger.error(e)
    return
