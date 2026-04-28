from fastapi import APIRouter, HTTPException
import hashlib
import database
from logs import log_activity

router = APIRouter()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register")
def register(email: str, password: str):
    existing_user = database.users_collection.find_one({"email": email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(password)

    database.users_collection.insert_one({
        "email": email,
        "password": hashed_password
    })

    log_activity(email, "User registered")

    return {"message": "User registered successfully"}


@router.post("/login")
def login(email: str, password: str):
    user = database.users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = hash_password(password)

    if user["password"] != hashed_password:
        raise HTTPException(status_code=400, detail="Invalid password")

    log_activity(email, "User logged in")

    return {"message": "Login successful"}