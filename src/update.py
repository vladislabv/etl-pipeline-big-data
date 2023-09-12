import pymongo
def updateInsert (collection, json):
  client = pymongo.MongoClient('mongodb+srv://marvin:9jZ05DgIh6qNeMrp@mongodbcluster.n6cun7v.mongodb.net/')
  db = client['MongoDB-Database']
  col = db[collection]

  query = {'_id': json['_id']}
  value = {'$set': json}

  x = col.update_one(query, value, upsert = True)

  client.close();
  return x