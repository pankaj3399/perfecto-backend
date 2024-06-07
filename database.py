# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DETAILS
import certifi

client = AsyncIOMotorClient(MONGO_DETAILS, tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
print(property_collection, 'xxxxx')