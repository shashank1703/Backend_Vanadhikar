from flask import Flask, jsonify, request
from flask_cors import CORS
from models.beneficiary_model import get_beneficiaries
from models.alert_model import add_alert
from scheduler import start_scheduler
from pymongo import MongoClient
from config import MONGO_URI


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "VanAdhikar DSS Backend is Running!"

client = MongoClient(MONGO_URI)
db = client["dss_db"]
collection = db["beneficiaries"]


@app.route('/api/beneficiaries', methods=['GET'])
def beneficiaries():
    district = request.args.get('district')
    print(district)
    block = request.args.get('block')
    print(block)
    village = request.args.get("village")
    
    # Build filter
    query = {}
    if district:
        query["district"] = district
    if block:
        query["block"] = block
    if village:
        query["village"] = village

    results = list(collection.find(query))
    
    # Convert ObjectId to string for JSON
    for r in results:
        r["_id"] = str(r["_id"])

    return jsonify(results)

@app.route('/api/alerts', methods=['GET'])
def alerts():
    beneficiaries = list(collection.find({}))
    alerts_list = []

    for b in beneficiaries:
        priority = "green"  # default low
        necessity = []      # list of missing necessities

        # Extract scheme data
        jjm = b.get("jjm_data", {})
        mgnrega = b.get("mgnrega_data", {})
        janman = b.get("pm_janman_data", {})

        connection_status = jjm.get("connection_status", True)
        days_provided = mgnrega.get("days_provided_fy", 0)
        days_demanded = mgnrega.get("days_demanded_fy", 1)
        has_pucca_house = janman.get("has_pucca_house", True)
        is_pvtg = janman.get("is_pvtg", False)

        # Fulfillment ratio
        fulfillment_ratio = days_provided / days_demanded if days_demanded > 0 else 0

        # Determine missing necessities and priority
        if not connection_status:
            necessity.append("water")
        if fulfillment_ratio < 0.5:
            necessity.append("employment")
        if not has_pucca_house:
            necessity.append("housing")

        # Priority rules
        if len(necessity) > 0:
            if "water" in necessity or fulfillment_ratio < 0.5 or not has_pucca_house:
                priority = "red"  # topmost
            elif 0.5 <= fulfillment_ratio < 0.8 or is_pvtg:
                priority = "orange"
        else:
            priority = "green"

        alerts_list.append({
            "name": b["name"],
            "district": b["district"],
            "block": b["block"],
            "village": b["village"],
            "priority": priority,
            "necessities": necessity
        })

    # Optional: Sort by priority (red > orange > green)
    priority_order = {"red": 0, "orange": 1, "green": 2}
    alerts_list.sort(key=lambda x: priority_order[x["priority"]])

    return jsonify(alerts_list)


if __name__ == '__main__':
    start_scheduler()  # Start background task
    app.run(debug=True)