from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# 1. Define the Database class
class Database:
    client: AsyncIOMotorClient = None

# 2. Instantiate the class
db = Database()

async def get_database():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    print("⏳ Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGO_DETAILS)
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    db.client.close()
    print("🛑 Closed MongoDB connection")