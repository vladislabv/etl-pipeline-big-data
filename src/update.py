import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')
db = client['MongoDB-Database']
colgateways = db["gateways"]
coltags = db["tags"]
colmeasures = db["measures2"]

def updateInsert (collection, json):
  
  if collection == "gateways":
    query = {'_id': json['_id']}
    value = {'$set': json}

    x = colgateways.update_one(query, value, upsert = True)

  if collection == "tags":
    query = {'_id': json['_id']}
    value = {'$set': json}

    x = coltags.update_one(query, value, upsert = True)

  if collection == "measures":
    query = {'recorded_time': json['recorded_time']}
    value = {'$set': json}

    x = colmeasures.insert_one(value)

  return x

def closeclient() :
  client.close()