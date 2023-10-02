from pymongo import MongoClient
from mongodb_env import load_env
from bson.objectid import ObjectId
from datetime import datetime
import matplotlib.pyplot as plt

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



'''
hier wird getestet, wie häufig neue Daten erfasst werden.
Wir haben in 0:29:59.19500 62280 measures erfasst,
sodass etwa 35 Measures pro Sekunde erfasst wurden.

Ohne print im Import-Code:
In etwa 10 Minuten 24308 measures, sodass etwa 40 
Measures pro Sekunde erfasst wurden.
'''
# select collection
collection = db['measures']

# Query the earliest and latest recorded times
earliest_recorded_time = collection.find_one({}, sort=[("recorded_time", 1)])["recorded_time"]
latest_recorded_time = collection.find_one({}, sort=[("recorded_time", -1)])["recorded_time"]

# Calculate the time difference
time_difference = latest_recorded_time - earliest_recorded_time

# Print the results
print(f"Earliest Recorded Time: {earliest_recorded_time}")
print(f"Latest Recorded Time: {latest_recorded_time}")
print(f"Time Difference: {time_difference}")

'''
This code deletes all documents from the specified collection

# select collection
collection = db['measures']
# Delete all documents from the collection
result = collection.delete_many({})
# Print the number of deleted documents
print(f"Deleted {result.deleted_count} documents from the collection.")
'''

'''
This code prints all tag_ids from the measurements
collection with their respective highest page number
'''
# select the collection
collection = db['measures']

# Define the aggregation pipeline
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
results = list(collection.aggregate(pipeline))

# Iterate through the results and print tag_id and max_page
for result in results:
    tag_id = result["_id"]
    max_page = result["max_page"]
    print(f"Tag ID: {tag_id}, Highest Page: {max_page}")



'''
Abfrage 1
In welcher Abteilung halten sich die meisten Kunden auf? 
Anzahl der Tags je Gateway ermitteln
Select gateway, count(tag_id)
'''
pipeline = [
    # Stage 1: Unwind the tags_assigned array
    {"$unwind": "$tags_assigned"},
    # Stage 2: Group by gateway_id and count the number of tags_assigned
    {
        "$group": {
            "_id": "$_id",
            "gateway_id": {"$first": "$_id"},
            "tag_count": {"$sum": 1}
        }
    },
    # Stage 3: Sort the result by tag_count in descending order
    {"$sort": {"tag_count": 1}},
    # Stage 4: Project the fields for the final result
    {"$project": {"_id": 0, "gateway_id": 1, "tag_count": 1}}
]


# Execute the aggregation query
results = list(gateways_collection.aggregate(pipeline))

# Print the results
for result in results:
    gateway_id = result["gateway_id"]
    tag_count = result["tag_count"]
    print(f"Gateway ID: {gateway_id}, Number of Tags Assigned: {tag_count}")


# Visualisierung der Abfrage
# extract data for plotting
gateway_ids = [result["gateway_id"] for result in results]
tag_counts = [result["tag_count"] for result in results]
mongodb_green = "#4DB33D"

# Create a horizontal bar chart
plt.barh(gateway_ids, tag_counts, color=mongodb_green)
plt.xlabel('Number of Tags Assigned')
plt.ylabel('Gateway ID')
plt.title('Number of Tags (customers) per Gateway (department)')
plt.show()


'''
Abfrage 2
Wie lange verbringt ein Kunde in einer Abteilung?
Zeitpunkte zwischen Gateway-Wechseln
Select gateway, avg time 
'''


'''
Abfrage 3
Wo gibt es viele Zusammenstöße mit den Regalen? 
Auf Acceleration über 200 m/s² nehmen - etwa 20g
Endergebnis
Select gateway, count(mesaures_über_20g)
'''


'''
Abfrage 4
Welche Abteilung hat die größten Acceleration Werte? 
Höhere Average Acceleration-Werte je Gateway wird als Kundeninteresse an Artikeln gedeutet
SELECT gateway, avg acceleartion je xyz 
'''





client.close()