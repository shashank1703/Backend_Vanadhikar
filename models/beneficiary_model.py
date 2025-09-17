from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["dss_db"]

def get_beneficiaries(filter_query):
    return list(db.beneficiaries.find(filter_query))

def get_beneficiary_by_id(b_id):
    return db.beneficiaries.find_one({"_id": b_id})
