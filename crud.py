# crud.py
from typing import List
from database import property_collection
from models import Property
import httpx
import os
scrapper_url = os.getenv("SCRAPPER_URL", "https://perfecto-scrapper.onrender.com/scrape/")


async def get_random_properties() -> List[Property]:
    properties_cursor = property_collection.aggregate([{"$sample": {"size": 3}}])
    properties = []
    async for property in properties_cursor:
        property["_id"] = str(property["_id"])
        properties.append(Property(**property))
    return properties

async def get_similar_properties() -> List[Property]:
    properties_cursor = property_collection.aggregate([{"$sample": {"size": 3}}])
    properties = []
    async for property in properties_cursor:
        property["_id"] = str(property["_id"])
        properties.append(Property(**property))
    return properties

async def fetch_data_from_url(url: str):
    timeout = httpx.Timeout(connect=60.0, read=30.0, write=30.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        print("scrapper_url", scrapper_url)
        response = await client.post(f"{scrapper_url}", json={"url": url})
        response.raise_for_status()
        print("response data", response.json())
        return response.json()
    