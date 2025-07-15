from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)


client = MongoClient("mongodb+srv://skillrank:project@<your-cluster>.mongodb.net/?retryWrites=true&w=majority")
db = client["donut_db"]
collection = db["batters"]


@app.route('/batter', methods=['POST'])
def add_batter():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Batter added", "id": str(result.inserted_id)}), 201


@app.route('/batter/<id>', methods=['GET'])
def read_batter(id):
    try:
        batter = collection.find_one({"_id": ObjectId(id)})
        if batter:
            batter["_id"] = str(batter["_id"])
            return jsonify(batter), 200
        return jsonify({"error": "Not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400


@app.route('/batter/<id>', methods=['PUT'])
def update_batter(id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.modified_count:
        return jsonify({"message": "Batter updated"}), 200
    return jsonify({"error": "Not found or no change"}), 404


@app.route('/batter/<id>', methods=['DELETE'])
def delete_batter(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Batter deleted"}), 200
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
