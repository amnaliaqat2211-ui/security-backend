from fastapi import APIRouter, HTTPException
import database

router = APIRouter()

# Update Profile
@router.post("/profile")
def update_profile(email: str, username: str, phone: str):
    user = database.users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    database.users_collection.update_one(
        {"email": email},
        {"$set": {"username": username, "phone": phone}}
    )

    return {"message": "Profile updated successfully"}


# Add Emergency Contact
@router.post("/add-contact")
def add_contact(email: str, name: str, phone: str):
    user = database.users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contact = {"name": name, "phone": phone}

    database.users_collection.update_one(
        {"email": email},
        {"$push": {"emergency_contacts": contact}}
    )

    return {"message": "Contact added successfully"}


# Get Profile
@router.get("/profile")
def get_profile(email: str):
    user = database.users_collection.find_one({"email": email}, {"_id": 0})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user