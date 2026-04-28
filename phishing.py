from fastapi import APIRouter
from logs import log_activity

router = APIRouter()

phishing_keywords = [
    "win money",
    "free prize",
    "click here",
    "urgent action",
    "bank alert",
    "verify account",
    "password reset",
    "lottery",
    "claim now"
]

@router.post("/detect-phishing")
def detect_phishing(message: str):
    message_lower = message.lower()

    score = 0

    for word in phishing_keywords:
        if word in message_lower:
            score += 1

    log_activity("unknown", "Phishing check performed")

    if score == 0:
        return {"status": "Safe", "confidence": "90%"}
    elif score <= 2:
        return {"status": "Suspicious", "confidence": "60%"}
    else:
        return {"status": "Malicious", "confidence": "95%"}