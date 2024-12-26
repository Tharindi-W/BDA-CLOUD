from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://e17299:gFH00zihG8Pjj0pX@meditrack.wg7uo.mongodb.net/?retryWrites=true&w=majority&appName=Meditrack")
db = client['MeditrackDB']
appointments_collection = db['Appointments']

# Base URL for NotificationService (adjust the host and port for your setup)
NOTIFICATION_SERVICE_URL = "http://notification-service:5002/notifications/schedule"

# Schedule a new appointment
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json

    # Insert the appointment into the database
    result = appointments_collection.insert_one(data)

    # Convert the inserted ObjectId to string for the response
    inserted_id = str(result.inserted_id)

    # Notify the NotificationService
    try:
        notification_response = requests.post(NOTIFICATION_SERVICE_URL, json=data)
        notification_status = notification_response.json()
    except requests.exceptions.RequestException as e:
        notification_status = {"error": f"Failed to send notification: {str(e)}"}

    return jsonify({
        "message": "Appointment scheduled successfully!",
        "appointment_id": inserted_id,  # Return the ObjectId as a string
        "notification_status": notification_status
    }), 201

# Get all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    # Retrieve all appointments from the database
    appointments = list(appointments_collection.find({}, {"_id": 1, "appointment_id": 1, "doctor_name": 1, "patient_name": 1, "date": 1, "time": 1, "condition": 1, "specialty": 1}))
    
    # Convert ObjectId to string
    for appointment in appointments:
        if "_id" in appointment:
            appointment["_id"] = str(appointment["_id"])

    return jsonify(appointments), 200

# Update an appointment
@app.route('/appointments/<id>', methods=['PUT'])
def update_appointment(id):
    data = request.json

    # Update the appointment in the database
    result = appointments_collection.update_one({"appointment_id": id}, {"$set": data})
    if result.matched_count:
        return jsonify({"message": "Appointment updated successfully!"}), 200
    else:
        return jsonify({"error": "Appointment not found!"}), 404

# Delete an appointment
@app.route('/appointments/<id>', methods=['DELETE'])
def delete_appointment(id):
    # Delete the appointment from the database
    result = appointments_collection.delete_one({"appointment_id": id})
    if result.deleted_count:
        return jsonify({"message": "Appointment deleted successfully!"}), 200
    else:
        return jsonify({"error": "Appointment not found!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
