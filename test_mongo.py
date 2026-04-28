from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://amnaliaqat2211_db_user:amna123@ac-stamuxw-shard-00-00.7kywthk.mongodb.net:27017,ac-stamuxw-shard-00-01.7kywthk.mongodb.net:27017,ac-stamuxw-shard-00-02.7kywthk.mongodb.net:27017/?ssl=true&replicaSet=atlas-uglvkz-shard-0&authSource=admin&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ Error:", e)