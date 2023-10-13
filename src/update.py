import os
import pymongo
from dotenv import load_dotenv

#load the .env file
load_dotenv()

#set the database-parameter
client = pymongo.MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')

#set the collections
db = client['MongoDB-Database']
colgateways = db["gateways"]
coltags = db["tags"]
colmeasures = db["measures"]

#delete all data from the database for a newstart test
def deleteMeasurements():
  colmeasures.delete_many({})
  coltags.delete_many({})
  colgateways.delete_many({})

  return 1

#get the last added page for a tag from the database
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

#check if the tag is already added and if there any changes in the changes return true
def checkLastTag(currentTag):
  result = coltags.find_one({'address': currentTag['address']}, sort=[('inserttimestamp', -1)])
  
  if not result:
    return True
  
  tempreturn = ((sorted(currentTag['config'].items()) != sorted(result['config'].items())) or (currentTag['online'] != result['online'])) 
  
  if tempreturn:
    print('Tag wird gespeichert')

  return tempreturn


#write the data to the database
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

#close the client connection at the end
def closeclient() :
  client.close()