import os
import json
import logging
import asyncio

import aiomqtt
import motor.motor_asyncio

import mongo_motor
from utils import convert_go_timestamp

logger = logging.getLogger(__name__)


async def assure_client_is_up(client):
    msg = await mongo_motor.ping_client(client)
    logger.info('MongoClient answered with %s' % msg)
    print(f"MongoClient answered with {msg}!")


async def assure_database_setup(client):
    db = client['admin']
    msg = await mongo_motor.setup_database(db)
    logger.info('MongoClient answered with %s' % msg)
    print(f"MongoClient answered with {msg}!")


async def process_gateway(msg, coll, s):
    document = json.loads(msg.payload.decode('utf-8'))
    document['last_contact'] = convert_go_timestamp(document['last_contact'])
    # uniqueness field
    reference_field = 'id'
    avoid_keys = ['last_contact']
    await mongo_motor.do_insert_on_change(
        conn=coll,
        d=document,
        ref_field=reference_field,
        avoid_keys=avoid_keys,
        s=s
    )


async def process_tag(msg, coll, s):
    document = json.loads(msg.payload.decode('utf-8'))
    document['last_contact'] = convert_go_timestamp(document['last_contact'])
    _ = document.pop('sensors', '')
    # uniqueness field
    reference_field = 'address'
    avoid_keys = ['last_contact']
    await mongo_motor.do_insert_on_change(
        conn=coll,
        d=document,
        ref_field=reference_field,
        avoid_keys=avoid_keys,
        s=s
    )


async def process_measure(msg, coll, s):
    document = json.loads(msg.payload.decode('utf-8'))
    document['recorded_time'] = convert_go_timestamp(document['recorded_time'])
    await mongo_motor.do_insert(
        conn=coll,
        document=document,
        session=s
    )


async def listen(mongo_client, port=1883, host="localhost", **kwargs):
    db = mongo_client['admin']
    async with await mongo_client.start_session() as s:
        async with aiomqtt.Client(hostname=host, port=port, **kwargs) as client:
            async with client.messages() as messages:
                await client.subscribe("gateways/+")
                await client.subscribe("tags/+")
                await client.subscribe("tags/+/measures")
                async for message in messages:
                    if message.topic.matches("gateways/+"):
                        await process_gateway(message, db['gateways'], s)
                    elif message.topic.matches("tags/+"):
                        await process_tag(message, db['tags'], s)
                    elif message.topic.matches("tags/+/measures"):
                        await process_measure(message, db['admin'], s)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(assure_client_is_up(mongo_client))
        tg.create_task(assure_database_setup(mongo_client))
        tg.create_task(
            listen(
                mongo_client=mongo_client,
                host=os.environ.get('MQTT_BROKER_HOST'),
                port=int(os.environ.get('MQTT_BROKER_PORT'))
            )
        )  # Start the listener task


if __name__ == '__main__':
    # logging settings
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='logs/live.log',
        filemode='a'
    )
    logger.info("Listener started successfully!")
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGO_URI'))
    asyncio.run(main())