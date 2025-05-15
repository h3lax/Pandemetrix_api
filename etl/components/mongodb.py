from pymongo import MongoClient, errors
from bson import json_util, ObjectId
from datetime import datetime

def insert_data(config, data, collection_name):
    try:
        client = MongoClient(
            host=config['host'],
            port=int(config.get('port', 27017)),
            username=config.get('username'),
            password=config.get('password')
        )
        db = client[config['database']]
        collection = db[collection_name]
        collection.insert_many(data.to_dict('records'))
        print(f"Data inserted into MongoDB collection '{collection_name}' successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def fetch_data(config, collection_name, query=None, skip=0, limit=1000):
    try:
        client = MongoClient(
            host=config['host'],
            port=config.get('port', 27017),
            username=config.get('username'),
            password=config.get('password')
        )
        db = client[config['database']]
        collection = db[collection_name]

        # Fetch the data with pagination
        cursor = collection.find(query or {}).skip(skip).limit(limit)

        # Convert each document to clean JSON
        data = []
        for doc in cursor:
            # Convert ObjectId to string
            doc['_id'] = str(doc['_id'])
            
            # Convert datetime to ISO string
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()

            data.append(doc)

        # Serialize the data to standard JSON
        json_data = json_util.dumps(data)

        return json_data
    
    except errors.PyMongoError as e:
        print(f"Error fetching data from MongoDB: {e}")
        return json_util.dumps({"error": str(e)})
    
    finally:
        client.close()