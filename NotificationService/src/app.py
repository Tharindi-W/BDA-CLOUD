from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://e17299:gFH00zihG8Pjj0pX@meditrack.wg7uo.mongodb.net/?retryWrites=true&w=majority&appName=Meditrack")
db = client['MeditrackDB']
appointments_collection = db['Appointments']

# Send a notification when an appointment is scheduled
@app.route('/notifications/schedule', methods=['POST'])
def send_scheduled_notification():
    data = request.json  # Expecting appointment data
    patient_name = data.get("patient_name")
    doctor_name = data.get("doctor_name")
    date = data.get("date")
    time = data.get("time")

    if not (patient_name and doctor_name and date and time):
        return jsonify({"error": "Incomplete data"}), 400

    # Example of a notification message
    notification_message = f"Hello {patient_name}, your appointment with Dr. {doctor_name} has been scheduled on {date} at {time}."
    print(notification_message)  # For now, we're just printing it (simulate SMS/email sending)
    return jsonify({"message": "Notification sent!", "details": notification_message}), 200

# Send reminders for upcoming appointments
@app.route('/notifications/reminders', methods=['GET'])
def send_reminders():
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")

    # Query MongoDB for tomorrow's appointments
    upcoming_appointments = appointments_collection.find({"date": tomorrow_date})
    reminders = []

    for appointment in upcoming_appointments:
        patient_name = appointment.get("patient_name")
        doctor_name = appointment.get("doctor_name")
        time = appointment.get("time")
        reminder_message = f"Reminder: Hello {patient_name}, you have an appointment with Dr. {doctor_name} tomorrow at {time}."
        print(reminder_message)  # Simulate sending the reminder
        reminders.append(reminder_message)

    return jsonify({"message": "Reminders sent!", "details": reminders}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
