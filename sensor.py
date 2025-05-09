from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

#client = MongoClient("mongodb://localhost:27017/")
# MongoDB connection
client = MongoClient("mongodb+srv://i40:dbms2@cluster0.lixbqmp.mongodb.net/")
db = client["sensorapp"]
collection = db["sensordata"]

@app.route('/')
def index():
    return "Flask server is running."

@app.route('/mongodb/post', methods=['POST'])
def post_gps_data():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        docs = [data] if isinstance(data, dict) else data if isinstance(data, list) else None
        if docs is None:
            return jsonify({"error": "Invalid JSON format"}), 400

        unsynced_docs = [doc for doc in docs if not doc.get("synced", False)]

        if not unsynced_docs:
            return jsonify({"message": "All data already synced."}), 200

        for doc in unsynced_docs:
            doc.pop("synced", None)  # Remove synced flag before inserting

        result = collection.insert_many(unsynced_docs)
        inserted_ids = [str(_id) for _id in result.inserted_ids]
        return jsonify({"message": "Inserted", "inserted_ids": inserted_ids}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
