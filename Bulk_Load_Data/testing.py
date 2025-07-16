import logging
import os
import time
from pymongo import MongoClient, DESCENDING
from tqdm import tqdm
from dotenv import load_dotenv


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("mongo_load_test.log"),
        logging.StreamHandler()
    ]
)

client = MongoClient(MONGO_URI)  
db = client[DATABASE_NAME]
collection = db["Testing"]


collection.create_index([("index", DESCENDING)])

def insert_records(total=1_000_000):
    logging.info(f"Inserting {total} records into MongoDB...")
    batch_size = 10_000

    for i in tqdm(range(0, total, batch_size), desc="Inserting records"):
        batch = [
            {
                "index": j,
                "data": f"Sample data {j}"
            }
            for j in range(i, min(i + batch_size, total))
        ]
        collection.insert_many(batch)

    logging.info(f"Successfully inserted {total} records.")

def delete_last_100_records():
    logging.info("Deleting last 100 inserted records (by index)...")
    to_delete = collection.find().sort("index", DESCENDING).limit(100)
    ids = [doc["_id"] for doc in to_delete]
    result = collection.delete_many({"_id": {"$in": ids}})
    logging.info(f"Deleted {result.deleted_count} records.")

if __name__ == "__main__":
    start = time.time()

    try:
        insert_records()
        delete_last_100_records()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    end = time.time()
    logging.info(f"Total execution time: {end - start:.2f} seconds")