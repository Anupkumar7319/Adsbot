All write ops centralized here so logic is easier to audit.
"""
from datetime import datetime, timedelta
from bson import ObjectId
from db import users_col, ads_col, impressions_col, withdrawals_col, now_utc
from config import CONFIG

# -----------------
# USERS
# -----------------

def get_or_create_user(user_id: int, username: str = None, lang: str = "en"):
    doc = users_col.find_one({'_id': user_id})
    if doc:
        return doc
    new_doc = {
        '_id': user_id,
        'username': username,
        'lang': lang,
        'coins': 0,
        'total_earned': 0,
        'referrer': None,
        'created_at': now_utc(),
        'last_ad_watch': None,
        'watch_counts': {},   # date string YYYY-MM-DD -> count
    }
    users_col.insert_one(new_doc)
    return new_doc


def get_user(user_id: int):
    return users_col.find_one({'_id': user_id})


def add_coins(user_id: int, coins: int):
    update = {
        '$inc': {'coins': coins, 'total_earned': coins},
        '$set': {'last_ad_watch': now_utc()}
    }
    users_col.update_one({'_id': user_id}, update, upsert=True)


def deduct_coins(user_id: int, coins: int) -> bool:
    user = get_user(user_id)
    if not user or user.get('coins', 0) < coins:
        return False
    users_col.update_one({'_id': user_id}, {'$inc': {'coins': -coins}})
    return True


def increment_watch_count(user_id: int):
    today = now_utc().strftime('%Y-%m-%d')
    users_col.update_one({'_id': user_id}, {'$inc': {f'watch_counts.{today}': 1}})


def get_today_watch_count(user_id: int) -> int:
    user = get_user(user_id)
    if not user:
        return 0
    today = now_utc().strftime('%Y-%m-%d')
    return user.get('watch_counts', {}).get(today, 0)

# -----------------
# ADS
# -----------------

def create_ad(title: str, ad_type: str = 'video', reward_coins: int = None, video_url: str = None,
              landing_url: str = None, daily_cap: int = 0, active: bool = True, cooldown_seconds: int = None):
    doc = {
        'title': title,
        'type': ad_type,  # video|link|cpa
        'reward_coins': reward_coins if reward_coins is not None else CONFIG.default_ad_reward,
        'video_url': video_url,
        'landing_url': landing_url,
        'daily_cap': daily_cap,  # 0 = unlimited
        'active': active,
        'cooldown_seconds': cooldown_seconds if cooldown_seconds is not None else CONFIG.ad_cooldown_seconds,
        'created_at': now_utc(),
    }
    res = ads_col.insert_one(doc)
    return str(res.inserted_id)


def get_active_ads():
    return list(ads_col.find({'active': True}))


def get_ad(ad_id: str):
    try:
        oid = ObjectId(ad_id)
    except Exception:
        return None
    return ads_col.find_one({'_id': oid})


def set_ad_active(ad_id: str, active: bool):
    oid = ObjectId(ad_id)
    ads_col.update_one({'_id': oid}, {'$set': {'active': active}})

# -----------------
# IMPRESSIONS
# -----------------

def record_impression(user_id: int, campaign_id: str, started: datetime = None):
    if started is None:
        started = now_utc()
    doc = {
        'user_id': user_id,
        'campaign_id': campaign_id,
        'created_at': started,
        'completed_at': None,
        'rewarded': False,
    }
    res = impressions_col.insert_one(doc)
    return str(res.inserted_id)


def mark_impression_completed(impression_id: str):
    oid = ObjectId(impression_id)
    impressions_col.update_one({'_id': oid}, {'$set': {'completed_at': now_utc()}})


def reward_impression(impression_id: str, user_id: int, coins: int):
    oid = ObjectId(impression_id)
    impressions_col.update_one({'_id': oid}, {'$set': {'rewarded': True, 'rewarded_at': now_utc(), 'reward_coins': coins}})
    add_coins(user_id, coins)
    increment_watch_count(user_id)


def last_completed_for_campaign(user_id: int, campaign_id: str):
    doc = impressions_col.find_one({'user_id': user_id, 'campaign_id': campaign_id, 'completed_at': {'$ne': None}}, sort=[('completed_at', -1)])
    return doc

# -----------------
# WITHDRAWALS
# -----------------

def create_withdrawal(user_id: int, amount_coins: int, upi_id: str):
    doc = {
        'user_id': user_id,
        'amount_coins': amount_coins,
        'amount_inr': round(amount_coins * CONFIG.coin_to_inr, 2),
        'upi_id': upi_id,
        'status': 'pending',  # pending|paid|rejected
        'requested_at': now_utc(),
        'processed_at': None,
    }
    res = withdrawals_col.insert_one(doc)
    return str(res.inserted_id)


def list_withdrawals(status: str = None, limit: int = 100):
    q = {}
    if status:
        q['status'] = status
    return list(withdrawals_col.find(q).sort('requested_at', -1).limit(limit))


def update_withdrawal_status(withdraw_id: str, status: str):
    oid = ObjectId(withdraw_id)
    withdrawals_col.update_one({'_id': oid}, {'$set': {'status': status, 'processed_at': now_utc()}})


def get_user_withdrawals(user_id: int, limit: int = 20):
    return list(withdrawals_col.find({'user_id': user_id}).sort('requested_at', -1).limit(limit))


---
