"""MongoDB connection + standard collections.
Create indexes on first import.
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from config import CONFIG

_client = MongoClient(CONFIG.mongo_uri)
db = _client[CONFIG.mongo_db]

# Collections
users_col = db["users"]
ads_col = db["ads"]
impressions_col = db["impressions"]
withdrawals_col = db["withdrawals"]
logs_col = db["logs"]

# Ensure indexes (idempotent)
users_col.create_index([("created_at", DESCENDING)])
users_col.create_index([("username", ASCENDING)])

ads_col.create_index([("active", ASCENDING)])
ads_col.create_index([("title", ASCENDING)])

impressions_col.create_index([("user_id", ASCENDING), ("campaign_id", ASCENDING), ("completed_at", DESCENDING)])
impressions_col.create_index([("created_at", DESCENDING)])

withdrawals_col.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
withdrawals_col.create_index([("requested_at", DESCENDING)])

# Basic heartbeat
if not db.command("ping"):
    raise RuntimeError("MongoDB ping failed")


def now_utc():
    return datetime.utcnow()


---
