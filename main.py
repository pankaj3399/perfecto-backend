# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from crud import get_random_properties, get_similar_properties
from bson import ObjectId
from database import property_collection
from models import Property
import uvicorn
from typing import List, Optional
import os

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
    status: Optional[str] = Query(None, enum=["Coming Soon", "Active", "Sold", "Pending"]),
    minLotSize: Optional[int] = Query(None),
    maxLotSize: Optional[int] = Query(None),
    minYearBuilt: Optional[int] = Query(None),
    maxYearBuilt: Optional[int] = Query(None)
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
        query["propertyListingDetails.status"] = status
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

    properties_cursor = property_collection.find(query)
    properties = []
    async for property in properties_cursor:
        property["_id"] = str(property["_id"])
        properties.append(Property(**property))
    return properties

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to port 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
