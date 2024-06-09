# database.py
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os

# TODO: finally remove this db url from here
client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"), tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
# print(property_collection, 'xxxxx')