import json
import os
import pymongo
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load env vars
load_dotenv()

try:
    # Load JSON data from file inside the JSON folder
    json_path = os.path.join("JSON", "ex5.json")
    with open(json_path, 'r') as file:
        data = json.load(file)

    # MongoDB Atlas connection from .env
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise Exception("Mongo URI not found in .env file")

    client = pymongo.MongoClient(mongo_uri)
    db = client["donutdb"]
    collection = db["donuts"]

    # Insert data
    if isinstance(data, list):
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")
    else:
        result = collection.insert_one(data)
        print(f"Inserted one document with ID: {result.inserted_id}")

except FileNotFoundError:
    print("❌ Error: ex5.json file not found.")
except json.JSONDecodeError:
    print("❌ Error: Failed to decode JSON. Please check the file format.")
except ConnectionFailure:
    print("❌ Error: Could not connect to MongoDB. Check your internet and connection string.")
except PyMongoError as e:
    print(f"❌ PyMongo Error: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
