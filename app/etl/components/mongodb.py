from pymongo import MongoClient, errors
from bson import json_util, ObjectId
from app.database.mongoClient import get_db
from datetime import datetime

def insert_data(data, collection_name):
    try:
        db = get_db()
        collection = db[collection_name]
        collection.insert_many(data.to_dict('records'))
        print(f"Data inserted into MongoDB collection '{collection_name}' successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def fetch_data(collection_name, query=None, skip=0, limit=1000):
    try:
        db = get_db()
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

def get_collection_names():
    try:
        db = get_db()
        return db.list_collection_names()
    except errors.PyMongoError as e:
        print(f"Error fetching collection names: {e}")
        return []
    
def get_collection_infos():
    try:
        db = get_db()
        collections = []
        for collection in db.list_collection_names():
            count = db[collection].count_documents({})
            collections.append({'collection': collection, 'count': count})
        return collections
    except errors.PyMongoError as e:
        print(f"Error fetching collection info: {e}")
        return []
