from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://e17299:gFH00zihG8Pjj0pX@meditrack.wg7uo.mongodb.net/?retryWrites=true&w=majority&appName=Meditrack")
db = client['MeditrackDB']
patients_collection = db['Patients']

# Add a new patient record
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json
    patients_collection.insert_one(data)
    return jsonify({"message": "Patient record added successfully!"}), 201

# Get all patient records
@app.route('/patients', methods=['GET'])
def get_patients():
    patients = list(patients_collection.find({}, {"_id": 0}))  # Exclude MongoDB ID from response
    return jsonify(patients), 200

# Update a patient record
@app.route('/patients/<name>', methods=['PUT'])
def update_patient(name):
    data = request.json
    result = patients_collection.update_one({"name": name}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Patient record updated successfully!"}), 200
    else:
        return jsonify({"error": "Patient not found!"}), 404

# Delete a patient record
@app.route('/patients/<name>', methods=['DELETE'])
def delete_patient(name):
    result = patients_collection.delete_one({"name": name})
    if result.deleted_count:
        return jsonify({"message": "Patient record deleted successfully!"}), 200
    else:
        return jsonify({"error": "Patient not found!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
