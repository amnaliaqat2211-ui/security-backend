from fastapi import APIRouter
from datetime import datetime
import database

router = APIRouter()

# Log activity
def log_activity(email: str, action: str):
    database.db["logs"].insert_one({
        "email": email,
        "action": action,
        "time": datetime.now()
    })

# Get all logs
@router.get("/logs")
def get_logs():
    logs = list(database.db["logs"].find({}, {"_id": 0}))
    return {"logs": logs}