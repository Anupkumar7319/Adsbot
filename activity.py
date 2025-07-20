from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mybotdb")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]


def update_user_activity(user_id, username=None):
    """
    Jab bhi user koi command ya action kare,
    uska last_active timestamp update karo.
    """
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": username,
                "last_active": datetime.utcnow()
            }
        },
        upsert=True
    )


def get_active_users(since_minutes=30):
    """
    Last X minutes ke andar active users ko return kare.
    Default 30 minutes hai.
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=since_minutes)
    active_users = list(users_collection.find({"last_active": {"$gte": cutoff_time}}))
    return active_users


def count_active_users(since_minutes=30):
    """
    Active users ka count return kare.
    """
    return len(get_active_users(since_minutes))
