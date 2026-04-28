from fastapi import APIRouter, HTTPException
import database
from logs import log_activity

router = APIRouter()

@router.post("/sos")
def send_sos(email: str, location: str):
    user = database.users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contacts = user.get("emergency_contacts", [])

    if not contacts:
        return {"message": "No emergency contacts found"}

    alerts = []

    for contact in contacts:
        alerts.append({
            "to": contact["phone"],
            "message": f"🚨 SOS Alert from {email}! Location: {location}"
        })

    log_activity(email, "SOS triggered")

    return {
        "status": "SOS sent",
        "alerts": alerts
    }