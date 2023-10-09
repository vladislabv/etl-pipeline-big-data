# Insert functions
  
def updateInsert (collection, json):

  query = {'_id': json['_id']}
  value = {'$set': json}

  x = collection.update_one(query, value, upsert = True)
  return x