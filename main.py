from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI,UploadFile,File
import shutil
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from twilio.rest import Client
from typing import List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
SECRET_KEY = os.getenv("SECRET_KEY")
from fastapi import APIRouter
router = APIRouter()
security = HTTPBearer()
from bson import ObjectId
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user = rs_collection.find_one({
            "email": payload["email"]
        })

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user   # ✅ REAL USER FROM DB

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# ✅ ADD FUNCTION HERE
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
import time
last_request_time = 0
import asyncio
import requests
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
account_sid = os.getenv("TWILIO_ACCOUT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number =os.getenv ("TWILIO_NUMBER")
receiver_number =os.getenv("RECIEVER_NUMBER")
twilio_client = Client(account_sid, auth_token)
API_KEY=os.getenv("API_KEY")
import re
VT_API_KEY = os.getenv("VT_API_KEY")
from pymongo import MongoClient
import os
db_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", db_url)   # debug
if not db_url:
    raise Exception("❌ DATABASE_URL NOT FOUND")
client = MongoClient(db_url)
db = client["security_app"]
rs_collection = db["users"]
users_collection = db["users"]
sos_collection = db["sos_history"]
# ===================== SECURITY =====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
# ===================== MODELS =====================
class Contact(BaseModel):
    name: str
    phone:str
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    contacts: List[Contact]
    sos_message: str = "Help me!"
class LoginRequest(BaseModel):
    email: str
    password: str

class UpdateProfile(BaseModel):
    email: str
    username: str
    phone: str


class DeleteContact(BaseModel):
    phone: str
class UpdateContact(BaseModel):
    old_phone: str
    name: str
    phone: str

class SOSRequest(BaseModel):
   latitude: float
   longitude: float
   message: str
   email:str

class ChatRequest(BaseModel):
    message: str
class URLRequest(BaseModel):
    url: str
from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str
# =======================
# 1. EXTRACT URLS
# =======================
def extract_urls(text):
    return re.findall(r'https?://\S+', text)
@app.post("/extract-and-scan")
async def extract_and_scan(data: TextRequest):
    urls = extract_urls(data.text)

    if not urls:
        return {"status": "error", "message": "No URLs found"}

    return {
        "status": "success",
        "urls": urls
    }




# ================= SMART ANALYSIS ENGINE =================

def analyze_message(text):
    text = text.lower()
    reasons = []
    score = 0

    patterns = {
        "otp": ("asks for OTP", 3),
        "password": ("asks for password", 3),
        "bank": ("asks for bank details", 3),
        "account": ("mentions sensitive account info", 2),
        "click": ("contains suspicious instruction", 2),
        "link": ("possible phishing link", 2),
        "urgent": ("creates urgency pressure", 2),
        "verify": ("asks for verification", 2),
        "winner": ("fake prize lure", 2),
        "lottery": ("lottery scam indicator", 2)
    }

    for key, (reason, value) in patterns.items():
        if key in text:
            reasons.append(reason)
            score += value

    if score >= 5:
        level = "HIGH"
    elif score >= 3:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, reasons, score


# ================= EMERGENCY =================

def detect_emergency(text):
    emergency_words = ["help", "danger", "attack", "save me", "kidnap"]
    return any(word in text.lower() for word in emergency_words)


def emergency_response():
    return (
        "🚨 EMERGENCY DETECTED!\n\n"
        "📍 Share your location immediately.\n"
        "📞 Call police or emergency services.\n"
        "⚠️ Stay safe and seek nearby help."
    )



# =================== REGISTER ===================
@app.post("/register")
def register(data: RegisterRequest):

    existing_user = users_collection.find_one({"email": data.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(data.password)

    users_collection.insert_one({
        "username": data.username,
        "email": data.email,
        "password": hashed,
        "contacts": [contact.dict() for contact in data.contacts],
        "sos_message": data.sos_message
    })

    return {"message": "User registered successfully"}
# ==========================
# 🔐 LOGIN API
# ==========================
@app.post("/login")
def login(data: LoginRequest):
    try:
        # 🔍 FIND USER
        user = users_collection.find_one({"email": data.email})

        if not user:
            return {"message": "User not found"}

        # 🔑 VERIFY PASSWORD
        if not verify_password(data.password, user["password"]):
            return {"message": "Invalid password"}

        # 🔐 CREATE TOKEN
        token_data = {
            "username": user.get("username"),
            "email": user.get("email"),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # ✅ FINAL RESPONSE
        return {
            "message": "Login successful",
            "username": user.get("username"),
            "email": user.get("email"),
            "contacts": user.get("contacts", []),
            "sos_message": user.get("sos_message", ""),
            "access_token": access_token   # 🔥 IMPORTANT
        }

    except Exception as e:
        print("🔥 LOGIN ERROR:", str(e))
        return {"detail": str(e)}

        


# ===================== UPDATE PROFILE =====================

@router.post("/update-profile")
def update_profile(data: UpdateProfile, current_user: dict = Depends(get_current_user)):

    result = rs_collection.update_one(
        {"_id": current_user["_id"]},   # 🔥 USE ID ONLY
        {"$set": {
            "username": data.username,
            "email": data.email,
            "phone": data.phone
        }}
    )

    # 🔥 CHECK IF UPDATE HAPPENED
    if result.modified_count == 0:
        return {"error": "Update failed or no changes made"}

    # 🔥 RETURN UPDATED DATA
    updated_user = rs_collection.find_one({"_id": current_user["_id"]})

    return {
        "username": updated_user["username"],
        "email": updated_user["email"],
        "phone": updated_user.get("phone", "")
    }


# ===================== UPDATE SOS =====================

@app.post("/sos")
def send_sos(data: SOSRequest):
    print("🚨 SOS TRIGGERED")
    print("Location:", data.latitude, data.longitude)

    # 🔥 GET USER CONTACTS FROM DATABASE
    user_data = users_collection.find_one({"email": data.email})
    if not user_data:
     return {"error":"User not founf"}
    contacts = user_data.get("contacts", [])

    # ✅ SAVE SOS HISTORY
    sos_collection.insert_one({
        "latitude": data.latitude,
        "longitude": data.longitude,
        "message": data.message,
        "contacts": contacts,
        "time": datetime.now()
    })

    # ✅ LOCATION LINK
    location_link = f"https://www.google.com/maps?q={data.latitude},{data.longitude}"

    # ✅ SMS BODY
    sms_body = f"""
🚨 EMERGENCY ALERT 🚨
Someone triggered SOS!

Location:
{location_link}

Message:
{data.message}
"""

    # 🔥 LOOP THROUGH CONTACTS (FROM DB NOW)
    for contact in contacts:
        number = contact["phone"]
        try:
            twilio_client.messages.create(
                body=sms_body,
                from_=twilio_number,
                to=number
            )
            print(f"SMS sent to {number}")
        except Exception as e:
            print(f"Failed for {number}: {e}")

    return {"status": "SOS sent to all contacts"}
        

 
# ===================== GET PROFILE =====================

@app.get("/get-profile/{email}")
def get_profile(email: str):

    user = users_collection.find_one({"email": email})

    if user:
        return {
            "username": user.get("username"),
            "email": user.get("email"),
            "contacts": user.get("contacts", []),
            "sos_message": user.get("sos_message", "")
        }
    else:
        return {"message": "User not found"}
    # ===================== URL EXTRACTOR =====================

def extract_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    return re.findall(url_pattern, text)
import random
import re

chat_history = []

# ===== INTENT DETECTION =====
def detect_intent(text):
    text = text.lower()

    if any(word in text for word in ["otp", "verification code"]):
        return "otp"
    elif any(word in text for word in ["phishing", "fake email", "fake link"]):
        return "phishing"
    elif any(word in text for word in ["scam", "fraud"]):
        return "scam"
    elif any(word in text for word in ["password"]):
        return "password"
    elif any(word in text for word in ["safe", "security", "protect"]):
        return "security"
    elif any(word in text for word in ["app", "application"]):
        return "app"
    elif any(word in text for word in ["sos", "emergency"]):
        return "sos"
    elif any(word in text for word in ["hack", "hacked"]):
        return "hacked"
    return None

# ================= SECURITY LOGIC =================

def smart_detect_threat(text):
    text = text.lower()

    if "otp" in text or "password" in text or "bank" in text:
        return "HIGH"

    if "verify" in text or "urgent" in text or "click link" in text:
        return "MEDIUM"

    return "LOW"


def detect_emergency(text):
    text = text.lower()
    words = ["help", "danger", "attack", "save me", "kidnap"]

    return any(word in text for word in words)


def emergency_response():
    return "🚨 Emergency detected! Please use SOS or contact authorities."


def extract_urls(text):
    return re.findall(r'https?://\S+', text)


def check_url(url):
    if "bit.ly" in url or "tinyurl" in url:
        return "⚠️ Suspicious shortened URL detected!"
    return None


# ================= FACT DETECTION =================

def is_factual_question(text):
    text = text.lower()

    question_words = [
        "who", "what", "when", "where",
        "current", "latest", "today",
        "president", "prime minister",
        "price", "news"
    ]

    return any(word in text for word in question_words)



def get_wikipedia_summary(query):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query +"current",
            "format": "json"
        }

        search_res = requests.get(search_url, params=params)
        search_data = search_res.json()

        if search_data.get("query", {}).get("search"):
            title = search_data["query"]["search"][0]["title"]

            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
            summary_res = requests.get(summary_url)
            summary_data = summary_res.json()

            if "extract" in summary_data:
                return summary_data["extract"]

    except Exception as e:
        print("Wiki error:", e)

    return None


# ================= CONFIDENCE =================

def get_confidence(score):
    if score >= 5:
        return "90%"
    elif score >= 3:
        return "70%"
    return "40%"


# ================= CHAT API =================
@app.post("/chat")
async def chat(req: ChatRequest):

    # ✅ ALWAYS DEFINE MESSAGE FIRST
    message = req.message.strip()
    print("User:", message)

    # ================== 1. ANALYSIS ==================
    level, reasons, score = analyze_message(message)
    confidence = get_confidence(score)

    if level == "HIGH":
        return {
            "reply": (
                "🚨 HIGH RISK DETECTED\n\n"
                f"🔍 Reasons: {', '.join(reasons)}\n"
                f"📊 Confidence: {confidence}\n\n"
                "⚠️ Do NOT share personal information!"
            )
        }

    elif level == "MEDIUM":
        return {
            "reply": (
                "⚠️ SUSPICIOUS MESSAGE\n\n"
                f"🔍 Reasons: {', '.join(reasons)}\n"
                f"📊 Confidence: {confidence}\n\n"
                "👉 Be cautious before taking action."
            )
        }

    # ================== 2. EMERGENCY ==================
    if detect_emergency(message):
        return {"reply": emergency_response()}

    # ================== 3. URL CHECK ==================
    urls = extract_urls(message)
    for url in urls:
        warning = check_url(url)
        if warning:
            return {"reply": warning}

    # ================== 4. WIKIPEDIA ==================
    wiki_result = get_wikipedia_summary(message)
    if wiki_result:
        return {
            "reply": "📚 Based on available information:\n\n" + wiki_result
        }

    # ================== 5. AI FALLBACK ==================
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI Security Assistant."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
        )

        result = response.json()
        print("OPENROUTER RESPONSE:", result)

        # ❗ show real error if API fails
        if "choices" not in result:
            return {"reply": f"⚠️ API Error: {result}"}

        return {
            "reply": result["choices"][0]["message"]["content"]
        }

    except Exception as e:
        print("CHAT ERROR:", e)
        return {"reply": f"⚠️ Server Error: {str(e)}"}

# =======================
# 2. SCAN URL
# =======================
@app.post("/scan-url")
async def scan_url(data: URLRequest):

    headers = {"x-apikey": VT_API_KEY.strip()}

    # Submit URL
    res = requests.post(
        "https://www.virustotal.com/api/v3/urls",
        headers=headers,
        data={"url": data.url}
    )

    if res.status_code != 200:
        return {"status": "error"}

    analysis_id = res.json()["data"]["id"]

    # Get result
    result = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
        headers=headers
    )

    stats = result.json()["data"]["attributes"]["stats"]

    if stats["malicious"] > 0:
        return {"status": "malicious"}
    elif stats["suspicious"] > 0:
        return {"status": "suspicious"}
    else:
        return {"status": "safe"}

# =======================
# 3. FILE SCAN
# =======================
@app.post("/scan-file")
async def scan_file(file: UploadFile = File(...)):
    global last_request_time

    current_time = time.time()

    # ⛔ prevent too fast requests
    if current_time - last_request_time < 10:
        return {
            "status": "ERROR",
            "message": "Please wait before scanning next file"
        }
    last_request_time = current_time

    try:
        headers = {"x-apikey": VT_API_KEY.strip()}

        file_bytes = await file.read()

        if not file_bytes:
            return {"status": "ERROR", "message": "Empty file"}

        files = {
            "file": (file.filename, file_bytes, "application/octet-stream")
        }

        # ✅ STEP 1: Upload only
        upload = requests.post(
            "https://www.virustotal.com/api/v3/files",
            headers=headers,
            files=files
        )

        print("UPLOAD RESPONSE:", upload.text)

        # ❌ HANDLE ERROR
        if upload.status_code != 200:
            error_text = upload.text.lower()

            if "rate limit" in error_text:
                message = "API limit reached. Try again in a few seconds."
            elif "size" in error_text:
                message = "File too large."
            else:
                message = "Upload failed due to API limitation."

            return {
                "status": "ERROR",
                "filename": file.filename,
                "message": message
            }

        # ✅ IMPORTANT: RETURN analysis_id
        analysis_id = upload.json()["data"]["id"]

        return {
            "status": "PROCESSING",
            "analysis_id": analysis_id,
            "filename": file.filename
        }

    except Exception as e:
        print("SCAN ERROR:", e)
        return {
            "status": "ERROR",
            "filename": file.filename,
            "message": "Something went wrong"
        }

        # ✅ 2. ADD THIS BELOW scan_file FUNCTION

@app.get("/check-status/{analysis_id}")
async def check_status(analysis_id: str):
    headers = {"x-apikey": VT_API_KEY.strip()}

    res = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
        headers=headers
    )

    data = res.json()["data"]["attributes"]

    if data["status"] != "completed":
        return {"status": "PROCESSING"}

    stats = data["stats"]

    if stats["malicious"] > 0:
        return {"status": "MALICIOUS", "details": stats}
    elif stats["suspicious"] > 0:
        return {"status": "SUSPICIOUS", "details": stats}
    else:
        return {"status": "SAFE", "details": stats}
@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    
    # Save audio file
    with open("audio.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🔥 TEMPORARY (for testing)
    return {
        "text": "Hello from backend (dummy response)"
    }
security = HTTPBearer()

# 🔐 Decode token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# ✅ PROFILE API
@app.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return {
        "username": user.get("username"),
        "email": user.get("email")
    }
@app.post("/add-contact")
def add_contact(contact: Contact, user=Depends(get_current_user)):
    users_collection.update_one(
        {"email": user["email"]},
        {"$push": {"contacts": contact.dict()}}
    )
    return {"message": "Contact added"}
@app.get("/contacts")
def get_contacts(user=Depends(get_current_user)):
    user_data = users_collection.find_one({"email": user["email"]})
    return {"contacts": user_data.get("contacts", [])}


@app.post("/delete-contact")
def delete_contact(data: DeleteContact, user=Depends(get_current_user)):
    users_collection.update_one(
        {"email": user["email"]},
        {"$pull": {"contacts": {"phone": data.phone}}}
    )
    return {"message": "Deleted"}


@app.post("/update-contact")
def update_contact(data: UpdateContact, user=Depends(get_current_user)):
    users_collection.update_one(
        {
            "email": user["email"],
            "contacts.phone": data.old_phone
        },
        {
            "$set": {
                "contacts.$.name": data.name,
                "contacts.$.phone": data.phone
            }
        }
    )
    return {"message": "Updated"}