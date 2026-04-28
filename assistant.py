from fastapi import APIRouter

router = APIRouter()

# Simple chatbot responses
def get_response(message: str):
    message = message.lower()

    if "hello" in message:
        return "Hello! How can I help you?"

    elif "help" in message:
        return "I can help you detect scams, scan URLs, or send SOS alerts."

    elif "scam" in message:
        return "If you receive suspicious messages, use phishing detection feature."

    elif "sos" in message:
        return "Press the SOS button to alert your emergency contacts."

    else:
        return "I'm here to assist you with your security needs."

# Chat API
@router.post("/chat")
def chat(message: str):
    response = get_response(message)
    return {"response": response}