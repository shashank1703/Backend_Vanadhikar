import json
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["dss_db"]
collection = db["beneficiaries"]

with open('data/dummy_beneficiaries.json') as f:
    data = json.load(f)

collection.delete_many({})
collection.insert_many(data)
print("Inserted", len(data),"documents into MongoDB")
print(db.list_collection_names())
beneciaries = db["beneficiaries"].find().limit(5)
for doc in beneciaries:
    print(doc)
print("Inserted", len(data),"documents into MongoDB")
