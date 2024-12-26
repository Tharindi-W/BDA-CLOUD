import requests

def test_patient_service():
    response = requests.get("http://meditrack.local/patients")
    assert response.status_code == 200

def test_notification_service_schedule():
    response = requests.post("http://meditrack.local/notifications/schedule", json={"data": "sample"})
    assert response.status_code == 200

def test_analytics_service_appointments_per_doctor():
    response = requests.get("http://meditrack.local/aggregation/appointments_per_doctor")
    assert response.status_code == 200

def test_appoinment_service():
    response = requests.get("http://meditrack.local/appointments")
    assert response.status_code == 200
