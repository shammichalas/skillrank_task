from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE = 'ex5.json'


def read_json():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as file:
        return json.load(file)


def write_json(data):
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/batter', methods=['POST'])
def add_batter():
    try:
        data = request.get_json()
        ex5 = read_json()

        for donut in ex5:
            if donut.get("name") == "Old Fashioned":
                donut["batters"]["batter"].append(data)
                write_json(ex5)
                return jsonify({"message": "Batter added successfully"}), 201

        return jsonify({"error": "Donut not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/batter/<id>', methods=['GET'])
def get_batter(id):
    try:
        ex5 = read_json()
        for donut in ex5:
            for batter in donut["batters"]["batter"]:
                if batter["id"] == id:
                    return jsonify(batter), 200
        return jsonify({"error": "Batter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/batter/<id>', methods=['PUT'])
def update_batter(id):
    try:
        new_data = request.get_json()
        ex5 = read_json()

        for donut in ex5:
            for batter in donut["batters"]["batter"]:
                if batter["id"] == id:
                    batter.update(new_data)
                    write_json(ex5)
                    return jsonify({"message": "Batter updated successfully"}), 200

        return jsonify({"error": "Batter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/batter/<id>', methods=['DELETE'])
def delete_batter(id):
    try:
        ex5 = read_json()

        for donut in ex5:
            for batter in donut["batters"]["batter"]:
                if batter["id"] == id:
                    donut["batters"]["batter"].remove(batter)
                    write_json(ex5)
                    return jsonify({"message": "Batter deleted successfully"}), 200

        return jsonify({"error": "Batter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
