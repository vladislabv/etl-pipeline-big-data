import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')
db = client['MongoDB-Database']
  
def updateInsert (collection, json):
  col = db[collection]

  query = {'_id': json['_id']}
  value = {'$set': json}

  x = col.update_one(query, value, upsert = True)
  return x

def closeclient() :
  client.close();