import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

load_dotenv()  # take environment variables from .env.

# client = load_env()
client = MongoClient('mongodb+srv://' + os.getenv('MongoUser') + ':' + os.getenv('MongoPassword') + '@mongodbcluster.n6cun7v.mongodb.net/')

for db_name in client.list_database_names():
    print(db_name)

db = client['MongoDB-Database']

gateways_collection = db['gateways']
measures_collection = db['measures']
tags_collection = db['tags']
mongodb_green = "#4DB33D"

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
Wo gibt es viele Zusammenstöße mit den Regalen? 
Auf Acceleration über 200 m/s² nehmen - etwa 20g
Endergebnis
Select gateway, count(*)
from gateway, left join tags_assigned on tag.tag_id left join measures.tag_id
where acc_x > 20g or acc_y > 20g or acc_z > 20g 
'''
pipeline = [
    # Stage 1: Filter documents where acc_x is above the threshold
    {
        "$match": {
            "acc_x": {"$gt": 200}
        }
    },
    # Stage 2: Group by gateway_id and count the documents
    {
        "$group": {
            "_id": "$gateway_id",
            "count_acc_x_above_20g": {"$sum": 1}
        }
    }
]

# Execute the aggregation query
results_acc_x = list(measures_collection.aggregate(pipeline))


pipeline = [
    # Stage 1: Filter documents where acc_x is above the threshold
    {
        "$match": {
            "acc_y": {"$gt": 200}
        }
    },
    # Stage 2: Group by gateway_id and count the documents
    {
        "$group": {
            "_id": "$gateway_id",
            "count_acc_y_above_20g": {"$sum": 1}
        }
    }
]

# Execute the aggregation query
results_acc_y = list(measures_collection.aggregate(pipeline))

# convert the results to a pandas DataFrame
df_acc_x_above_threshold = pd.DataFrame(results_acc_x)
df_acc_y_above_threshold = pd.DataFrame(results_acc_y)

# Sort the DataFrame by the count values and filter on top 5 results
df_sorted_acc_x = df_acc_x_above_threshold.sort_values(by='count_acc_x_above_20g', ascending=False).head(5).sort_values(by='count_acc_x_above_20g', ascending=True)
df_sorted_acc_y = df_acc_y_above_threshold.sort_values(by='count_acc_y_above_20g', ascending=False).head(5).sort_values(by='count_acc_y_above_20g', ascending=True)

plt.figure(figsize=(10, 6))
# Plot x data
plt.subplot(2, 1, 1)
plt.barh(df_sorted_acc_x['_id'], df_sorted_acc_x['count_acc_x_above_20g'], color=mongodb_green)
plt.xlabel('Count of acc_x above 20G')
plt.ylabel('Gateway ID')
plt.title('Top 5 Gateways with the Most acc_x Above 20G')

plt.subplot(2, 1, 2)
plt.barh(df_sorted_acc_y['_id'], df_sorted_acc_y['count_acc_y_above_20g'], color=mongodb_green)
plt.xlabel('Count of acc_y above 20G')
plt.ylabel('Gateway ID')
plt.title('Top 5 Gateways with the Most acc_y Above 20G')
plt.tight_layout()
plt.show()


'''
Abfrage 3
Welche Abteilung hat die größten Acceleration Werte? 
Höhere Average Acceleration-Werte je Gateway wird als Kundeninteresse an Artikeln gedeutet
SELECT gateway, avg(measures.acc_x), avg(measures.acc_y), avg(measures.acc_z)
from gateway, left join tags_assigned on tag.tag_id left join measures.tag_id
'''

pipeline = [
    # Stage 1: Group by gateway_id and calculate average for each field
    {
        "$group": {
            "_id": "$gateway_id",
            "avg_acc_x": {"$avg": "$acc_x"},
            "avg_acc_y": {"$avg": "$acc_y"},
            "avg_acc_z": {"$avg": "$acc_z"}
        }
    }
]

# Execute the aggregation query
results = list(measures_collection.aggregate(pipeline))

# Print the results
for result in results:
    gateway_id = result["_id"]  # Use "_id" as it is the grouped field
    avg_acc_x = result["avg_acc_x"]
    avg_acc_y = result["avg_acc_y"]
    avg_acc_z = result["avg_acc_z"]
    print(f"Gateway ID: {gateway_id}, Average acc_x: {avg_acc_x}, Average acc_y: {avg_acc_y}, Average acc_z: {avg_acc_z}")

# Extract data for visualization
gateway_ids = [result["_id"] for result in results]
avg_acc_x_values = [result["avg_acc_x"] for result in results]
avg_acc_y_values = [result["avg_acc_y"] for result in results]
avg_acc_z_values = [result["avg_acc_z"] for result in results]


# Visualization
# Convert the results to a pandas DataFrame
df = pd.DataFrame(results)

# Sort the DataFrame by average acceleration values and filter on top 5 results
df_sorted_x = df.sort_values(by='avg_acc_x', ascending=False).head(5).sort_values(by='avg_acc_x', ascending=True)
df_sorted_y = df.sort_values(by='avg_acc_y', ascending=False).head(5).sort_values(by='avg_acc_y', ascending=True)
df_sorted_z = df.sort_values(by='avg_acc_z', ascending=False).head(5).sort_values(by='avg_acc_z', ascending=True)

# Plotting horizontal bar graphs for top 5 gateways
plt.figure(figsize=(10, 6))

# Plot for acc_x
plt.subplot(2, 1, 1)
plt.barh(df_sorted_x['_id'], df_sorted_x['avg_acc_x'], color=mongodb_green)
plt.yticks(df_sorted_x['_id'], df_sorted_x['_id'])
plt.xlabel('Average acc_x')
plt.title('Top 5 Gateways - Average Acceleration in X Direction')

# Plot for acc_y
plt.subplot(2, 1, 2)
plt.barh(df_sorted_y['_id'], df_sorted_y['avg_acc_y'], color=mongodb_green)
plt.yticks(df_sorted_y['_id'], df_sorted_y['_id'])
plt.xlabel('Average acc_y')
plt.title('Top 5 Gateways - Average Acceleration in Y Direction')

plt.tight_layout()
plt.show()

'''
Abfrage 4
Wie lange verbringt ein Kunde in einer Abteilung?
Zeitpunkte zwischen Gateway-Wechseln
Select gateway, avg time 
'''

# Define a projection to retrieve only the desired fields
projection = {
    "_id": 0,  # Exclude the MongoDB document ID
    "recorded_time": 1,
    "gateway_id": 1,
    "tag_id": "$tag_address",  # Assuming tag_id is stored in the tag_address field
}

# Fetch documents with the specified projection
cursor = measures_collection.find({}, projection)

# Convert the cursor to a list and then to a DataFrame
measures_df = pd.DataFrame(list(cursor))

# Convert recorded_time to datetime format
measures_df["recorded_time"] = pd.to_datetime(measures_df["recorded_time"])

# Sort the DataFrame by recorded_time
measures_df.sort_values(by="recorded_time", inplace=True)

# Calculate the time difference between consecutive records for the same tag_id and gateway_id
measures_df["time_diff"]= measures_df.groupby(["tag_id", "gateway_id"])["recorded_time"].diff()

# Identify distinct connection events (cases where the time difference is greater than 1 minute)
time_threshold = pd.Timedelta(minutes=1)
measures_df["new_connection_event"] = (measures_df["time_diff"] > time_threshold).astype(int)

# Cumulative sum of new_connection_event to create groups
measures_df["connection_event_group"] = measures_df.groupby("gateway_id")["new_connection_event"].cumsum()

# Calculate the total connection time for each gateway_id and connection_event_group
total_connection_time = measures_df.groupby(["gateway_id", "connection_event_group"])["recorded_time"].agg(["min", "max"]).reset_index()

# Calculate the average connection time for each gateway_id
average_connection_time = total_connection_time.copy()
average_connection_time["duration"] = average_connection_time["max"] - average_connection_time["min"]
average_connection_time["average_connection_time"] = average_connection_time["duration"] / pd.Timedelta(seconds=1)  # Convert to seconds for average

# Sort the DataFrame by average_connection_time in descending order
average_connection_time_sorted = average_connection_time.sort_values(by='average_connection_time', ascending=False)

'''Below is the visualisation code'''
# Group by gateway_id and calculate the average connection time
grouped_gateways = average_connection_time_sorted.groupby('gateway_id')['average_connection_time'].mean().reset_index()

# Sort the grouped DataFrame by average connection time in descending order
grouped_gateways_sorted = grouped_gateways.sort_values(by='average_connection_time', ascending=False)

# Display the result
print(grouped_gateways_sorted[["gateway_id", "average_connection_time"]])

# Top 5 gateways
top5_gateways = grouped_gateways_sorted.head(5).sort_values(by='average_connection_time', ascending=True)

# Bottom 5 gateways
bottom5_gateways = grouped_gateways_sorted.tail(5).sort_values(by='average_connection_time', ascending=True)

# Visualization
plt.figure(figsize=(10, 6))

# Top 5
plt.subplot(2, 1, 1)
plt.barh(top5_gateways['gateway_id'], top5_gateways['average_connection_time'], color=mongodb_green)
plt.yticks(top5_gateways['gateway_id'], top5_gateways['gateway_id'])
plt.xlabel('Average Connection Time (s)')
plt.title('Top 5 Gateways by Average Connection Time')

# Bottom 5
plt.subplot(2, 1, 2)
plt.barh(bottom5_gateways['gateway_id'], bottom5_gateways['average_connection_time'], color=mongodb_green)
plt.yticks(bottom5_gateways['gateway_id'], bottom5_gateways['gateway_id'])
plt.xlabel('Average Connection Time (s)')
plt.title('Bottom 5 Gateways by Average Connection Time')

# Adjust layout
plt.tight_layout()
plt.show()


client.close()