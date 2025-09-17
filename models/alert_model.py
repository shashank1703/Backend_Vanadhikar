from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client["dss_db"]

def add_alert(beneficiary_id, alert_type, description, priority="High"):
    existing = db.alerts.find_one({
        "beneficiary_id": beneficiary_id,
        "alert_type": alert_type,
        "status": "New"
    })
    if not existing:
        db.alerts.insert_one({
            "beneficiary_id": beneficiary_id,
            "alert_type": alert_type,
            "description": description,
            "priority": priority,
            "status": "New",
            "createdAt": datetime.utcnow()
        })
