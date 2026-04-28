from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import GEO2D
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "pet_track"
    
    class Config:
        env_file = ".env"

settings = Settings()

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Create indexes for optimal performance
        await create_indexes()
        
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Users collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("username", unique=True)
        
        # Pets collection indexes
        await db.database.pets.create_index("owner_id")
        await db.database.pets.create_index("status")
        await db.database.pets.create_index("breed")
        await db.database.pets.create_index("color")
        await db.database.pets.create_index([("location", "2dsphere")])  # Geospatial index
        await db.database.pets.create_index("created_at")
        await db.database.pets.create_index([("status", "created_at")])
        
        # Matches collection indexes
        await db.database.matches.create_index("lost_pet_id")
        await db.database.matches.create_index("found_pet_id")
        await db.database.matches.create_index("match_score")
        await db.database.matches.create_index("status")
        await db.database.matches.create_index("created_at")
        
        # Notifications collection indexes
        await db.database.notifications.create_index("user_id")
        await db.database.notifications.create_index("created_at")
        await db.database.notifications.create_index([("user_id", "in_app_read")])
        
        # Contacts collection indexes
        await db.database.contacts.create_index("match_id")
        await db.database.contacts.create_index("initiator_id")
        await db.database.contacts.create_index("recipient_id")
        await db.database.contacts.create_index("status")
        
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Failed to create indexes: {e}")

# Collection getters
def get_users_collection():
    return db.database.users

def get_pets_collection():
    return db.database.pets

def get_matches_collection():
    return db.database.matches

def get_notifications_collection():
    return db.database.notifications

def get_contacts_collection():
    return db.database.contacts
