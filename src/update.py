import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')
db = client['MongoDB-Database']
colgateways = db["gateways"]
coltags = db["tags"]
colmeasures = db["measures"]

def deleteMeasurements():
  colmeasures.delete_many({})
  coltags.delete_many({})
  colgateways.delete_many({})

  return 1

def getLastPageNumber(tag_id):
  
  max_page = 1
  pipeline = [
    # Stage 1: Group documents by 'tag_id' and find the max 'page' in each group
    {
        "$group": {
            "_id": "$tag_id",
            "max_page": {"$max": "$page"}
        }
    }
  ]

  # Execute the aggregation query
  results = list(colmeasures.aggregate(pipeline))

  # Iterate through the results and print tag_id and max_page
  if len(results) > 0:
    for result in results:
      if result["_id"] == tag_id:
        max_page = result["max_page"]
      
  return max_page

def checkLastTag(currentTag):
  result = coltags.find_one({'address': currentTag['address']}, sort=[('inserttimestamp', -1)])
  
  if not result:
    return True
  
  tempreturn = ((sorted(currentTag['config'].items()) != sorted(result['config'].items())) or (currentTag['online'] != result['online'])) 
  
  if tempreturn:
    print('Tag wird gespeichert')

  return tempreturn



def updateInsert (collection, json):
  
  if collection == "gateways":
    query = {'_id': json['_id']}
    value = {'$set': json}

    x = colgateways.update_one(query, value, upsert = True)

  if collection == "tags":
    x = coltags.insert_one(json)

  if collection == "measures":
    x = colmeasures.insert_one(json)

  return x

def closeclient() :
  client.close()