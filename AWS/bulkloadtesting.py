import os
import time
import logging
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv

# Load .env only when running locally
if os.environ.get("AWS_EXECUTION_ENV") is None:
    load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Environment Variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = "Testing"

def get_db_collection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        raise

def insert_records(event):
    try:
        total = int(event.get("total", 1000))
        batch_size = int(event.get("batch_size", 100))
        collection = get_db_collection()
        logging.info(f"Inserting {total} records...")

        for i in range(0, total, batch_size):
            batch = [{"index": j, "data": f"Sample data {j}"} for j in range(i, min(i + batch_size, total))]
            collection.insert_many(batch)

        return {"statusCode": 200, "body": f"Inserted {total} records successfully"}
    except Exception as e:
        logging.error(f"Insertion failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def delete_last_n(event):
    try:
        limit = int(event.get("limit", 100))
        collection = get_db_collection()

        to_delete = collection.find().sort("index", DESCENDING).limit(limit)
        ids = [doc["_id"] for doc in to_delete]
        result = collection.delete_many({"_id": {"$in": ids}})

        return {"statusCode": 200, "body": f"Deleted {result.deleted_count} records."}
    except Exception as e:
        logging.error(f"Deletion failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def read_test(event):
    try:
        collection = get_db_collection()
        mode = event.get("mode", "single")
        start_time = time.time()

        if mode == "single":
            result = collection.find_one({"index": event.get("index", 500)})
        elif mode == "range":
            result = list(collection.find({
                "index": {"$gte": event.get("start", 100), "$lte": event.get("end", 200)}
            }))
        elif mode == "scan":
            result = list(collection.find({"data": {"$regex": "Sample"}}))
        else:
            return {"statusCode": 400, "body": "Invalid mode"}

        elapsed = time.time() - start_time
        count = len(result) if isinstance(result, list) else (1 if result else 0)

        return {
            "statusCode": 200,
            "body": f"Query ({mode}) returned {count} records in {elapsed:.2f}s"
        }
    except Exception as e:
        logging.error(f"Read test failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def lambda_handler(event, context):
    action = event.get("action")
    logging.info(f"Received action: {action}")

    if action == "insert":
        return insert_records(event)
    elif action == "delete":
        return delete_last_n(event)
    elif action == "read":
        return read_test(event)
    else:
        return {"statusCode": 400, "body": "Invalid or missing action. Use 'insert', 'delete', or 'read'."}
