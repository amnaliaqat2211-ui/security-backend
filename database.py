from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["ai_security_app"]

users_collection = db["users"]