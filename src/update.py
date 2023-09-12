import pymongo
from dotenv import load_dotenv

load_dotenv()

def updateInsert (collection, json):
  client = pymongo.MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')
  db = client['MongoDB-Database']
  col = db[collection]

  query = {'_id': json['_id']}
  value = {'$set': json}

  x = col.update_one(query, value, upsert = True)

  client.close();
  return x