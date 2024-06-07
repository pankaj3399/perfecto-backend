# crud.py
from typing import List
from database import property_collection
from models import Property

async def get_random_properties() -> List[Property]:
    properties_cursor = property_collection.aggregate([{"$sample": {"size": 3}}])
    properties = []
    async for property in properties_cursor:
        property["_id"] = str(property["_id"])
        properties.append(Property(**property))
    return properties
