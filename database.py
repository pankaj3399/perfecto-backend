# database.py
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os

# TODO: finally remove this db url from here
client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS", "mongodb+srv://prkskrs:1JRRLP0TScJtklaB@cluster0.fncdhdb.mongodb.net/perfecto?retryWrites=true&w=majority"), tlsCAFile=certifi.where())
database = client.perfecto
property_collection = database.get_collection("properties")
user_collection = database.get_collection("users")
requested_property_collection = database.get_collection("requested_properties")
referral_collection = database.get_collection("referrals")

# print(property_collection, 'xxxxx')