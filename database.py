import os
from pymongo import MongoClient

db_url = os.getenv("DATABASE_URL")

print("DATABASE_URL:", db_url)

if not db_url:
    raise Exception("❌ DATABASE_URL NOT FOUND")

client = MongoClient(db_url)

db = client["security_app"]
users_collection = db["users"]
sos_collection = db["sos_history"]