from flask import Flask, jsonify
from pymongo import MongoClient
import psycopg2
from collections import Counter


app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://e17299:gFH00zihG8Pjj0pX@meditrack.wg7uo.mongodb.net/?retryWrites=true&w=majority&appName=Meditrack"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['MeditrackDB']
appointments_collection = mongo_db['Appointments']

# Redshift Configuration
REDSHIFT_HOST = "myredshiftcluster.csqajvgqkn5v.us-east-1.redshift.amazonaws.com"
REDSHIFT_PORT = 5439
REDSHIFT_DBNAME = "analyticsdb"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = "E17299$sde"

# Function to connect to Redshift
def get_redshift_connection():
    try:
        conn = psycopg2.connect(
            host=REDSHIFT_HOST,
            port=REDSHIFT_PORT,
            dbname=REDSHIFT_DBNAME,
            user=REDSHIFT_USER,
            password=REDSHIFT_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Redshift: {e}")
        return None

# Endpoint to sync aggregated data to Redshift: Appointments Per Doctor
@app.route('/sync/appointments_per_doctor', methods=['POST'])
def sync_appointments_per_doctor():
    try:
        # Aggregate data from MongoDB
        pipeline = [
            {"$group": {"_id": "$doctor_name", "appointment_count": {"$sum": 1}}}
        ]
        results = list(appointments_collection.aggregate(pipeline))

        # Post data to Redshift
        conn = get_redshift_connection()
        if not conn:
            return jsonify({"error": "Redshift connection failed"}), 500
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments_per_doctor (
                doctor_name VARCHAR(255),
                appointment_count INT
            )
        """)
        conn.commit()

        for result in results:
            cursor.execute(
                """
                INSERT INTO appointments_per_doctor (doctor_name, appointment_count)
                VALUES (%s, %s)
                """,
                (result["_id"], result["appointment_count"])
            )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Appointments per doctor synced to Redshift"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to sync aggregated data to Redshift: Appointments Over Time
@app.route('/sync/appointments_over_time', methods=['POST'])
def sync_appointments_over_time():
    try:
        # Aggregate data from MongoDB
        pipeline = [
            {"$group": {"_id": "$date", "appointment_count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        results = list(appointments_collection.aggregate(pipeline))

        # Post data to Redshift
        conn = get_redshift_connection()
        if not conn:
            return jsonify({"error": "Redshift connection failed"}), 500
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments_over_time (
                appointment_date DATE,
                appointment_count INT
            )
        """)
        conn.commit()

        for result in results:
            cursor.execute(
                """
                INSERT INTO appointments_over_time (appointment_date, appointment_count)
                VALUES (%s, %s)
                """,
                (result["_id"], result["appointment_count"])
            )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Appointments over time synced to Redshift"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to sync aggregated data to Redshift: Common Conditions by Specialty
@app.route('/sync/common_conditions_by_specialty', methods=['POST'])
def sync_common_conditions_by_specialty():
    try:
        # Step 1: Aggregate data from MongoDB
        pipeline = [
            {"$group": {"_id": "$specialty", "conditions": {"$push": "$condition"}}}
        ]
        results = list(appointments_collection.aggregate(pipeline))

        # Step 2: Process data to calculate counts (similar to your GET endpoint)
        categorized_conditions = {
            specialty["_id"] or "Unknown": dict(Counter(filter(None, specialty["conditions"])))
            for specialty in results
        }

        # Step 3: Post data to Redshift
        conn = get_redshift_connection()
        if not conn:
            return jsonify({"error": "Redshift connection failed"}), 500
        cursor = conn.cursor()

        # Create table in Redshift if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS common_conditions_by_specialty (
                specialty VARCHAR(255),
                condition VARCHAR(255),
                count INT
            )
        """)
        conn.commit()

        # Step 4: Insert aggregated data into Redshift
        for specialty, conditions in categorized_conditions.items():
            for condition, count in conditions.items():
                cursor.execute(
                    """
                    INSERT INTO common_conditions_by_specialty (specialty, condition, count)
                    VALUES (%s, %s, %s)
                    """,
                    (specialty, condition, count)
                )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Common conditions by specialty synced to Redshift"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to sync aggregated data to Redshift: Average Appointments Per Patient
@app.route('/sync/average_appointments_per_patient', methods=['POST'])
def sync_average_appointments_per_patient():
    try:
        # Aggregate data from MongoDB
        pipeline = [
            {"$group": {"_id": "$patient_name", "appointment_count": {"$sum": 1}}},
            {"$group": {"_id": None, "average_appointments": {"$avg": "$appointment_count"}}}
        ]
        results = list(appointments_collection.aggregate(pipeline))
        average = results[0]["average_appointments"] if results else 0

        # Post data to Redshift
        conn = get_redshift_connection()
        if not conn:
            return jsonify({"error": "Redshift connection failed"}), 500
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS average_appointments_per_patient (
                average_appointments FLOAT
            )
        """)
        conn.commit()

        cursor.execute(
            """
            INSERT INTO average_appointments_per_patient (average_appointments)
            VALUES (%s)
            """,
            (average,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Average appointments per patient synced to Redshift"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
