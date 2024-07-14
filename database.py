# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi
import os

# Load .env file
load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"), tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
user_collection = database.get_collection("users")
requested_property_collection = database.get_collection("requested_properties")
referral_collection = database.get_collection("referrals")

# print(property_collection, 'xxxxx')