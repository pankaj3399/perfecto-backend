# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DETAILS
import certifi
import os

print(os.getenv("MONGO_DETAILS", 8000), 'Hi')

client = AsyncIOMotorClient(MONGO_DETAILS, tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
print(property_collection, 'xxxxx')