from flask import Flask, jsonify
from pymongo import MongoClient
from collections import Counter

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://e17299:gFH00zihG8Pjj0pX@meditrack.wg7uo.mongodb.net/?retryWrites=true&w=majority&appName=Meditrack")
db = client['MeditrackDB']
appointments_collection = db['Appointments']

# Number of appointments per doctor
@app.route('/aggregation/appointments_per_doctor', methods=['GET'])
def appointments_per_doctor():
    pipeline = [
        {"$group": {"_id": "$doctor_name", "appointment_count": {"$sum": 1}}}
    ]
    results = list(appointments_collection.aggregate(pipeline))
    return jsonify({"appointments_per_doctor": results}), 200

# Frequency of appointments over time
@app.route('/aggregation/appointments_over_time', methods=['GET'])
def appointments_over_time():
    pipeline = [
        {"$group": {"_id": "$date", "appointment_count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}  # Sort by date
    ]
    results = list(appointments_collection.aggregate(pipeline))
    return jsonify({"appointments_over_time": results}), 200

@app.route('/aggregation/common_conditions_by_specialty', methods=['GET'])
def common_conditions_by_specialty():
    pipeline = [
        {"$group": {"_id": "$specialty", "conditions": {"$push": "$condition"}}}
    ]
    results = list(appointments_collection.aggregate(pipeline))
    
    # Handle None values and avoid TypeError
    categorized_conditions = {
        specialty["_id"] or "Unknown": dict(Counter(filter(None, specialty["conditions"])))
        for specialty in results
    }
        # Return the response with the categorized conditions
    return jsonify({"common_conditions_by_specialty": categorized_conditions}), 200

# Average appointments per patient
@app.route('/aggregation/average_appointments_per_patient', methods=['GET'])
def average_appointments_per_patient():
    pipeline = [
        {"$group": {"_id": "$patient_name", "appointment_count": {"$sum": 1}}},
        {"$group": {"_id": None, "average_appointments": {"$avg": "$appointment_count"}}}
    ]
    results = list(appointments_collection.aggregate(pipeline))
    average = results[0]["average_appointments"] if results else 0
    return jsonify({"average_appointments_per_patient": average}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
