from app import app
from flask import Flask, request, jsonify
from datetime import datetime

data = {
    "users": {},
    "categories": {},
    "records": {},
}
user_id_counter = 1
category_id_counter = 1
record_id_counter = 1

@app.route("/healthcheck")
def healthcheck():
    current_time = datetime.now().isoformat()
    response = {
            'status': 'healthy',
            'timestamp': current_time
    }
    return jsonify(response), 200


@app.route("/user", methods=["POST"])
def create_user():
    global user_id_counter
    name = request.json.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    user_id = user_id_counter
    data["users"][user_id] = {"id": user_id, "name": name}
    user_id_counter += 1
    return jsonify(data["users"][user_id]), 201

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = data["users"].get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id not in data["users"]:
        return jsonify({"error": "User not found"}), 404
    del data["users"][user_id]
    return "", 204

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(list(data["users"].values()))


