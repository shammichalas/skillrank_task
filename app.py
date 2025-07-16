from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["donutdb"]
collection = db["donuts"]


@app.route("/donut", methods=["POST"])
def add_donut():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = collection.insert_one(data)
        return jsonify({"message": "Donut added", "id": str(result.inserted_id)}), 201
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/donut", methods=["GET"])
def get_all_donuts():
    try:
        donuts = list(collection.find({}, {"_id": 0}))
        return jsonify(donuts), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/donut/<string:donut_id>", methods=["GET"])
def get_donut(donut_id):
    try:
        result = collection.find_one({"id": donut_id}, {"_id": 0})
        if not result:
            return jsonify({"error": "Donut not found"}), 404
        return jsonify(result), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/donut/<string:donut_id>", methods=["PUT"])
def update_donut(donut_id):
    try:
        update_data = request.get_json()
        result = collection.update_one({"id": donut_id}, {"$set": update_data})
        if result.matched_count == 0:
            return jsonify({"error": "Donut not found"}), 404
        return jsonify({"message": "Donut updated"}), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/donut/<string:donut_id>", methods=["DELETE"])
def delete_donut(donut_id):
    try:
        result = collection.delete_one({"id": donut_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Donut not found"}), 404
        return jsonify({"message": "Donut deleted"}), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "Donut API is running 🍩"


if __name__ == "__main__":
    app.run(debug=True)
