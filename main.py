# main.py
from fastapi import FastAPI, HTTPException, Query, Depends, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from crud import get_random_properties, get_similar_properties
from bson import ObjectId
from database import property_collection, user_collection, requested_property_collection, referral_collection  
from models import Property, ContactForm, User, UserInDB, Token, RequestedProperty,AddressList
from auth import authenticate_user, create_access_token, get_current_user, get_password_hash
import uvicorn
from typing import List, Optional
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
import re
from datetime import timedelta
import string
import random


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class PropertyStatus(str, Enum):
    coming_soon = "Coming Soon"
    active = "Active"
    sold = "Sold"
    pending = "Pending"


app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.post("/signup", response_model=User)
async def create_user(user: UserInDB, referral_code: Optional[str] = None):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not referral_code:
        while True:
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            existing_code = await user_collection.find_one({"referral_code": referral_code})
            if not existing_code:
                break

    user.password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["_id"] = str(ObjectId())
    user_dict["referral_code"] = referral_code
    await user_collection.insert_one(user_dict)

    if user.referral_code:
        referrer = await user_collection.find_one({"referral_code": user.referral_code})
        if referrer:
            referral_data = {
                "_id": str(ObjectId()),
                "referrer_by": referrer["full_name"],
                "referrer_id": ObjectId(referrer["_id"]),
                "referred_user_id": ObjectId(user_dict["_id"]),
                "referred_user_name": user_dict["full_name"]
            }
            await referral_collection.insert_one(referral_data)

    return User(**user_dict)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password, form_data.scopes[0])
    print(user, 'user')
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "scopes": [user.role]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/recommendedProperties", response_model=List[Property])
async def recommended_properties():
    properties = await get_random_properties()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found")   
    return properties
    # wishlist = set(current_user.wishlist)
    
    # properties_with_wishlist_flag = []
    # for property in properties:
    #     property_dict = property.dict()
    #     property_dict['wishlisted'] = str(property_dict['id']) in wishlist
    #     property_dict['_id'] = str(property_dict['id'])
    #     properties_with_wishlist_flag.append(property_dict)
    # return properties_with_wishlist_flag

@app.get("/similarProperties", response_model=List[Property])
async def similar_properties():
    properties = await get_similar_properties()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found")
    return properties

@app.get("/property/{property_id}", response_model=Property)
async def get_property(property_id: str):
    if not ObjectId.is_valid(property_id):
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    document = await property_collection.find_one({"_id": ObjectId(property_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="Property not found")
    
    document["_id"] = str(document["_id"])

    return document

@app.get("/search", response_model=List[Property])
async def search_properties(
    address: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    minPrice: Optional[float] = Query(None),
    maxPrice: Optional[float] = Query(None),
    minBeds: Optional[int] = Query(None),
    maxBeds: Optional[int] = Query(None),
    minBaths: Optional[int] = Query(None),
    maxBaths: Optional[int] = Query(None),
    minSqft: Optional[int] = Query(None),
    maxSqft: Optional[int] = Query(None),
    status: Optional[List[PropertyStatus]] = Query(None),
    minLotSize: Optional[int] = Query(None),
    maxLotSize: Optional[int] = Query(None),
    minYearBuilt: Optional[int] = Query(None),
    maxYearBuilt: Optional[int] = Query(None),
    minLat: Optional[float] = None,
    maxLat: Optional[float] = None,
    minLng: Optional[float] = None,
    maxLng: Optional[float] = None,
):
    match_stage = {}

    if address:
        match_stage["address"] = re.compile(f".*{address}.*", re.IGNORECASE)
    
    if city:
        match_stage["city"] = city
    
    if minPrice is not None and maxPrice is not None:
        match_stage["price"] = {"$gte": minPrice, "$lte": maxPrice}
    elif minPrice is not None:
        match_stage["price"] = {"$gte": minPrice}
    elif maxPrice is not None:
        match_stage["price"] = {"$lte": maxPrice}
    
    if minBeds is not None and maxBeds is not None:
        match_stage["beds"] = {"$gte": minBeds, "$lte": maxBeds}
    elif minBeds is not None:
        match_stage["beds"] = {"$gte": minBeds}
    elif maxBeds is not None:
        match_stage["beds"] = {"$lte": maxBeds}
    
    if minBaths is not None and maxBaths is not None:
        match_stage["baths"] = {"$gte": minBaths, "$lte": maxBaths}
    elif minBaths is not None:
        match_stage["baths"] = {"$gte": minBaths}
    elif maxBaths is not None:
        match_stage["baths"] = {"$lte": maxBaths}
    
    if minSqft is not None and maxSqft is not None:
        match_stage["sqft"] = {"$gte": minSqft, "$lte": maxSqft}
    elif minSqft is not None:
        match_stage["sqft"] = {"$gte": minSqft}
    elif maxSqft is not None:
        match_stage["sqft"] = {"$lte": maxSqft}
    
    if status:
        match_stage["propertyListingDetails.status"] = {"$in": status}
    
    if minLotSize is not None and maxLotSize is not None:
        match_stage["homeFacts.lotSize"] = {"$gte": minLotSize, "$lte": maxLotSize}
    elif minLotSize is not None:
        match_stage["homeFacts.lotSize"] = {"$gte": minLotSize}
    elif maxLotSize is not None:
        match_stage["homeFacts.lotSize"] = {"$lte": maxLotSize}
    
    if minYearBuilt is not None and maxYearBuilt is not None:
        match_stage["homeFacts.yearBuilt"] = {"$gte": minYearBuilt, "$lte": maxYearBuilt}
    elif minYearBuilt is not None:
        match_stage["homeFacts.yearBuilt"] = {"$gte": minYearBuilt}
    elif maxYearBuilt is not None:
        match_stage["homeFacts.yearBuilt"] = {"$lte": maxYearBuilt}
    
    if minLat is not None and maxLat is not None:
        match_stage["latitude"] = {"$gte": minLat, "$lte": maxLat}
    elif minLat is not None:
        match_stage["latitude"] = {"$gte": minLat}
    elif maxLat is not None:
        match_stage["latitude"] = {"$lte": maxLat}

    if minLng is not None and maxLng is not None:
        match_stage["longitude"] = {"$gte": minLng, "$lte": maxLng}
    elif minLng is not None:
        match_stage["longitude"] = {"$gte": minLng}
    elif maxLng is not None:
        match_stage["longitude"] = {"$lte": maxLng}
    
    pipeline = [
        {"$addFields": {
            "latitude": {"$toDouble": "$latitude"},
            "longitude": {"$toDouble": "$longitude"},
            "homeFacts.lotSize": {"$toDouble": "$homeFacts.lotSize"},
            "homeFacts.yearBuilt": {"$toDouble": "$homeFacts.yearBuilt"},
        }},
        {"$match": match_stage}
    ]

    properties = []
    async for property in property_collection.aggregate(pipeline):
        property["_id"] = str(property["_id"])
        properties.append(Property(**property))
    
    return properties


@app.post("/contact")
async def contact(contact_form: ContactForm):
    # Replace the following with your email and app password
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    to_email = "iitgncli@gmail.com"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = contact_form.email
    msg['To'] = to_email
    msg['Subject'] = "New Contact Form Submission"
    
    body = f"""
    Name: {contact_form.name}
    Email: {contact_form.email}
    Phone: {contact_form.phone}
    Description: {contact_form.description}
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submitAddresses", response_model=List[RequestedProperty])
async def submit_addresses(address_list: AddressList,  current_user: dict = Depends(get_current_user)):
    print(current_user, 'Hi')
    if current_user.role != 'agent':
        raise HTTPException(status_code=403, detail="Not authorized")

    requested_properties = []

    for address in address_list.addresses:
        requested_property = {
            "address": address,
            "agent_id": str(current_user.id),
            "status": "pending",
            "_id": str(ObjectId())
        }
        await requested_property_collection.insert_one(requested_property)
        requested_properties.append(RequestedProperty(**requested_property))

    return requested_properties

@app.get("/requestedProperties", response_model=List[RequestedProperty])
async def get_requested_properties(status: str = "pending", current_user: dict = Depends(get_current_user)):
    # if current_user['role'] != 'agent':
    #     raise HTTPException(status_code=403, detail="Not authorized")
    
    requested_properties = []
    async for property in requested_property_collection.find({"status": status}):
        property["_id"] = str(property["_id"])
        requested_properties.append(RequestedProperty(**property))
    
    return requested_properties

# wishlist apis
@app.post("/wishlist/add/{property_id}", response_model=User)
async def add_to_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
    print('wishlist add' ,current_user)
    print('Current wishlist:', current_user.wishlist)
    if not property_id:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    if property_id in current_user.wishlist:
        raise HTTPException(status_code=400, detail="Property already in wishlist")

    await user_collection.update_one(
        {"_id": current_user.id},
        {"$push": {"wishlist": property_id}}
    )
    current_user.wishlist.append(property_id)
    return current_user

@app.post("/wishlist/remove/{property_id}", response_model=User)
async def remove_from_wishlist(property_id: str, current_user: User = Depends(get_current_user)):
    if not property_id:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    if property_id not in current_user.wishlist:
        raise HTTPException(status_code=400, detail="Property not in wishlist")

    await user_collection.update_one(
        {"_id": current_user.id},
        {"$pull": {"wishlist": property_id}}
    )

    current_user.wishlist.remove(property_id)
    return current_user

@app.get("/wishlist", response_model=List[Property])
async def get_wishlist(current_user: User = Depends(get_current_user)):
    properties = []
    for property_id in current_user.wishlist:
        document = await property_collection.find_one({"_id": ObjectId(property_id)})
        if document:
            document["_id"] = str(document["_id"])
            properties.append(Property(**document))
    return properties

@app.post("/property/{property_id}/reject", response_model=dict)
async def reject_requested_property(property_id: str = Path(..., description="The ID of the requested property to reject"),
                                    current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can reject properties")

    updated_property = await requested_property_collection.find_one_and_update(
        {"_id": ObjectId(property_id)},
        {"$set": {"status": "rejected"}},
        return_document=True
    )

    if not updated_property:
        raise HTTPException(status_code=404, detail="Requested property not found")

    updated_property["_id"] = str(updated_property["_id"])
    return updated_property

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to port 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
