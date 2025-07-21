import os
import time
import json
import logging
from pymongo import MongoClient, DESCENDING





# Setup Logging
logging.basicConfig(level=logging.INFO)

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

def create_record(event):
    try:
        body = json.loads(event.get("body", "{}"))
        total = int(body.get("total", 1000))
        batch_size = int(body.get("batch_size", 100))
        collection = get_db_collection()

        for i in range(0, total, batch_size):
            batch = [{"index": j, "data": f"Sample data {j}"} for j in range(i, min(i + batch_size, total))]
            collection.insert_many(batch)

        return {"statusCode": 200, "body": json.dumps({"message": f"Inserted {total} records successfully"})}
    except Exception as e:
        logging.error(f"Insertion failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def get_record(event):
    try:
        query_params = event.get("queryStringParameters", {}) or {}
        collection = get_db_collection()
        mode = query_params.get("mode", "single")
        start_time = time.time()

        if mode == "single":
            index = int(query_params.get("index", 500))
            result = collection.find_one({"index": index})
            data = result if result else {}
        elif mode == "range":
            start = int(query_params.get("start", 100))
            end = int(query_params.get("end", 200))
            data = list(collection.find({"index": {"$gte": start, "$lte": end}}))
        elif mode == "scan":
            data = list(collection.find({"data": {"$regex": "Sample"}}))
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid mode"})}

        elapsed = time.time() - start_time
        count = len(data) if isinstance(data, list) else (1 if data else 0)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "count": count,
                "duration": f"{elapsed:.2f}s",
                "data": data
            }, default=str)
        }
    except Exception as e:
        logging.error(f"Read failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def update_record(event):
    try:
        body = json.loads(event.get("body", "{}"))
        index = body.get("index")
        new_data = body.get("data")

        if index is None or new_data is None:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing 'index' or 'data'"})}

        collection = get_db_collection()
        result = collection.update_one({"index": index}, {"$set": {"data": new_data}})

        return {
            "statusCode": 200,
            "body": json.dumps({"matched": result.matched_count, "modified": result.modified_count})
        }
    except Exception as e:
        logging.error(f"Update failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def delete_record(event):
    try:
        query_params = event.get("queryStringParameters", {}) or {}
        limit = int(query_params.get("limit", 100))
        collection = get_db_collection()

        to_delete = collection.find().sort("index", DESCENDING).limit(limit)
        ids = [doc["_id"] for doc in to_delete]
        result = collection.delete_many({"_id": {"$in": ids}})

        return {"statusCode": 200, "body": json.dumps({"deleted": result.deleted_count})}
    except Exception as e:
        logging.error(f"Deletion failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def lambda_handler(event, context):
    try:
        method = event.get("httpMethod")
        path = event.get("path")

        logging.info(f"Incoming request: {method} {path}")

        if method == "POST" and path == "/create":
            return create_record(event)
        elif method == "GET" and path == "/get":
            return get_record(event)
        elif method == "PUT" and path == "/update":
            return update_record(event)
        elif method == "DELETE" and path == "/delete":
            return delete_record(event)
        else:
            return {"statusCode": 404, "body": json.dumps({"error": "Invalid path or method"})}
    except Exception as e:
        logging.error(f"Request handling failed: {e}")
        return {"statusCode": 500, "body": str(e)}
