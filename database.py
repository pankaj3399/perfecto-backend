# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DETAILS
import certifi
import os


client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS", "mongodb+srv://pranavpawar3:hTS0nJvSKjPANicc@cluster0.tdgygtb.mongodb.net"), tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
print(property_collection, 'xxxxx')