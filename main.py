# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from crud import get_random_properties, get_similar_properties
from bson import ObjectId
from database import property_collection
from models import Property, ContactForm
import uvicorn
from typing import List, Optional
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum

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

@app.get("/recommendedProperties", response_model=List[Property])
async def recommended_properties():
    properties = await get_random_properties()
    if not properties:
        raise HTTPException(status_code=404, detail="No properties found")
    return properties

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
    query = {}

    if address:
        query["address"] = {"$regex": address, "$options": "i"}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if minPrice is not None and maxPrice is not None:
        query["price"] = {"$gte": minPrice, "$lte": maxPrice}
    elif minPrice is not None:
        query["price"] = {"$gte": minPrice}
    elif maxPrice is not None:
        query["price"] = {"$lte": maxPrice}
    if minBeds is not None and maxBeds is not None:
        query["beds"] = {"$gte": minBeds, "$lte": maxBeds}
    elif minBeds is not None:
        query["beds"] = {"$gte": minBeds}
    elif maxBeds is not None:
        query["beds"] = {"$lte": maxBeds}
    if minBaths is not None and maxBaths is not None:
        query["baths"] = {"$gte": minBaths, "$lte": maxBaths}
    elif minBaths is not None:
        query["baths"] = {"$gte": minBaths}
    elif maxBaths is not None:
        query["baths"] = {"$lte": maxBaths}
    if minSqft is not None and maxSqft is not None:
        query["sqft"] = {"$gte": minSqft, "$lte": maxSqft}
    elif minSqft is not None:
        query["sqft"] = {"$gte": minSqft}
    elif maxSqft is not None:
        query["sqft"] = {"$lte": maxSqft}
    if status:
        query["propertyListingDetails.status"] = {"$in": status}
    if minLotSize is not None and maxLotSize is not None:
        query["homeFacts.lotSize"] = {"$gte": str(minLotSize), "$lte": str(maxLotSize)}
    elif minLotSize is not None:
        query["homeFacts.lotSize"] = {"$gte": str(minLotSize)}
    elif maxLotSize is not None:
        query["homeFacts.lotSize"] = {"$lte": str(maxLotSize)}
    if minYearBuilt is not None and maxYearBuilt is not None:
        query["homeFacts.yearBuilt"] = {"$gte": str(minYearBuilt), "$lte": str(maxYearBuilt)}
    elif minYearBuilt is not None:
        query["homeFacts.yearBuilt"] = {"$gte": str(minYearBuilt)}
    elif maxYearBuilt is not None:
        query["homeFacts.yearBuilt"] = {"$lte": str(maxYearBuilt)}
    if minLat is not None and maxLat is not None:
        query["latitude"] = {"$gte": minLat, "$lte": maxLat}
    elif minLat is not None:
        query["latitude"] = {"$gte": minLat}
    elif maxLat is not None:
        query["latitude"] = {"$lte": maxLat}

    if minLng is not None and maxLng is not None:
        query["longitude"] = {"$gte": minLng, "$lte": maxLng}
    elif minLng is not None:
        query["longitude"] = {"$gte": minLng}
    elif maxLng is not None:
        query["longitude"] = {"$lte": maxLng}

    properties_cursor = property_collection.find(query)
    properties = []
    async for property in properties_cursor:
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to port 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
