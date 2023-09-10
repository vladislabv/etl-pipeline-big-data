from pymongo import MongoClient
from mongodb_env import load_env
from bson.objectid import ObjectId
from datetime import datetime

client = load_env()

for db_name in client.list_database_names():
    print(db_name)

db = client['MongoDB-Database']

gateways_collection = db['gateways']
measures_collection = db['measures']
tags_collection = db['tags']

# query some document from a collection
documents_to_find = {}
one_document = gateways_collection.find_one(documents_to_find)
print(one_document)

# query and print all documents of a collection
cursor = measures_collection.find()
num_docs = 0
for document in cursor:
        num_docs += 1
        print(document)
print("number of documents found: " + str(num_docs))

# extract the name of all gateways
cursor = tags_collection.find()
for document in cursor:
    name = document.get("name")
    print(name)


"""
The following code block is an example query. It calculates the average temperature per day
based on the measurements in the measures collection. 
"""
# Define the aggregation stages as strings
# Stage 1: Project the date part of recorded_time and temperature
stage1 = {
    "$project": {
        "date": {
            "$dateToString": {
                "format": "%Y-%m-%d",
                "date": "$recorded_time"
            }
        },
        "temperature": 1
    }
}

# Stage 2: Group documents by date and calculate the average temperature
stage2 = {
    "$group": {
        "_id": "$date",
        "average_temperature": {
            "$avg": "$temperature"
        }
    }
}

# Stage 3: Sort the results by date in ascending order
stage3 = {
    "$sort": {
        "_id": 1
    }
}

# Construct the aggregation pipeline
pipeline = [stage1, stage2, stage3]

# Execute the aggregation query
results = measures_collection.aggregate(pipeline)

# Print the average temperature per day
for result in results:
    date = result["_id"]
    average_temperature = result["average_temperature"]
    print(f"Date: {date}, Average Temperature: {average_temperature:.2f}°C")

# above code as a function with input_date as input to only 
# show the average temperature for a specific day 
def get_average_temperature_for_date(input_date):
    # Define the aggregation stages as strings
    stage1 = {
        "$project": {
            "date": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$recorded_time"
                }
            },
            "temperature": 1
        }
    }

    stage2 = {
        "$group": {
            "_id": "$date",
            "average_temperature": {
                "$avg": "$temperature"
            }
        }
    }

    stage3 = {
        "$sort": {
            "_id": 1
        }
    }

    # Construct the aggregation pipeline
    pipeline = [stage1, stage2, stage3]

    # Execute the aggregation query
    results = measures_collection.aggregate(pipeline)

    # Search for the input date in the results
    for result in results:
        date = result["_id"]
        if date == input_date:
            average_temperature = result["average_temperature"]
            print(f"Date: {date}, Average Temperature: {average_temperature:.2f}°C")
            return

    # If the input date is not found in the results
    print(f"No data found for date: {input_date}")

# Example usage:
# Replace '2023-09-09' with the date you want to query.
get_average_temperature_for_date('2023-09-09')
get_average_temperature_for_date('2023-09-02')
get_average_temperature_for_date('2023-09-01')

client.close()