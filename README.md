# Experiment on scaling the Project "Databases in BigData (MongoDB)"

This README will explain the main concepts which were implemented in this branch, which is (temporarily) not compartible with the main part of the project.
This part of the project is (still) in development, therefore we cannot guarantee it is functioning in the way, the main branch does.

Before starting the work on this experiment, we were facing some problems:
    1. The way we processing the data is hardly scalable
    2. Everything runs in a syncronous way, which slows the processing even more
    3. Every break in processing will lead to unpredictable results
    4. We cannot guarantee that the processing will work on different systems

Thinking of it, led us to the concept which has to solve (or soften) the problems we faced.

Idea 1: Every task should be isolated. (Single-responsibility principle)

Idea 2: Everything that can run asyncronously, should run asyncronously.

Idea 3: Every task may fail, nevertheless we shouldn't loose any data.


Based on the ideas, it led us to new tools that we brought to the project:

1. Docker: A tool helps by module isolation. As of now, It should be also possible use it for scaling.

2. MQTT Message Broker (Mosquitto): A message broker using mqtt protocol, lightweight but still powerfull. Main task - organizing extracted data for further processing.

3. Node-red: A platform written on Node.js, meaning everything happens parallelly. Also provides UI to work with the way you need to construct the processing, like block-schemas.


Docker consists of following containers (modules):

**mosquitto**
Eclipse Mosquitto is an open source (EPL/EDL licensed) message broker that implements the MQTT protocol versions 5.0, 3.1.1 and 3.1. Mosquitto is lightweight and is suitable for use on all devices from low power single board computers to full servers.

Needed as temporary storage for incoming data from ruuvi-tags, also structures the stream of data to be easily written to a long-storage (MongoDB)


**db**
A source-available cross-platform document-oriented database program. Classified as a NoSQL database program, MongoDB uses JSON-like documents with optional schemas.

Database schema used can be found [here](https://dbdocs.io/stasenko_vladislav/new-database-schema-mongodb?view=table_structure)


**node-red**
A programming tool for wiring together hardware devices, APIs and online services. It provides a browser-based editor that makes it easy to wire together flows using the wide range of nodes in the palette that can be deployed to its runtime in a single-click.

Processing steps:

1. Introduce trigger message, which will start the whole pipeline on schedule (So can we control the frequency on updating gateways, tags or measures)

2. Ask the API to list all available gateways, convert output to JSON and put every single gateway to a message topic "gateway/<gatewayid>"

3. Receive incoming gateways (as messages), and by using the gatewayid ask API for all tags are connected to the gateway

4. Process tags, save "gatewayid" into the message payload, and insert every as a single message into a topic "tags/<tagaddress>",

5. Receive incoming tags (as messages), and by using the gatewayid and tagaddress, start asking for measurements

6. First of all, check a key-value database if there is a key with the gateway id with page number, if not start pagination at page 1.

7. Run while loop with the condition that the API output is empty or the number of items < 10.

8. Each loop asks for measures at combination gatewayid-tagaddress-page, on success saves the progress for the given tagaddress to the key-value database and starts processing the measures. On failure it comes to the next tag.

9. The processed measures are saved into a message topic "tags/<tagaddress>/measures"


**python-listener**
Lightweight python module, which uses aiomtqq in order to process incoming messages from mosquitto in asyncronous way. Also saving / reading to / from MongoDB happens in async way, thanks to motor & asyncio combination.

Processing steps:

1. Check if MongoDB database if available and make collections setup (add validation rules and needed indices if not done previously).

2. Subscribe to each topic to listen to coming messages.

3. Save tags as well gateways only if it doesn't exist (based on gatewayid or tagaddress) or some fields are changed.

4. Insert every coming measure.

**mongo-Express**
A web-based MongoDB admin interface written with Node.js, Express, and Bootstrap3.

Used for controlling incoming data and run available queries for getting first insights on the data.


Advantages of new processing way:

1. Can be easily brought to the cloud services like Docker Swarm, AWS ECS and others. (Therefore no need using MongoCluster)

2. Due to Isolation it can be (easily?) upscaled:

    1. Node-red: Holding additional instances of node-red may be helpful on breakdowns of the main instance. Due to centralized key-value database, the pagination over measurements will be continued correctly.
    2. Mosquitto: Provides such features as Quality-of-Service, Will messages and message replication to assure that no data is lost if the broker is down.
    3. Python-listener: Acknowledges data duplicates, therefore multiple instances can be run in parallel, for example each asking main or message broker replica(s). A handling of late-arriving messages can be additionally added.

3. Asyncronous processing saves time and enables reducing message queue.












        



This repository serves for a project proposed by Fachhochschule Suedwestfalen, subject "Datenbanken in Big Data"
