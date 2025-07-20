"""Configuration loader for Watch Ads & Earn Bot.
Reads environment variables, applies defaults, and exposes structured config.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # loads from .env if present

# --- Required Telegram credentials ---
API_ID = int(os.getenv("API_ID", 0))          # e.g. 123456
API_HASH = os.getenv("API_HASH", "")          # e.g. 'abcd1234...'
BOT_TOKEN = os.getenv("BOT_TOKEN", "")        # BotFather token

# --- MongoDB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "earn_bot")

# --- Web / Hosting ---
# Public base URL where your Flask app is reachable (Render/GCP/etc.)
# Example: https://your-app.onrender.com
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Used to sign reward tokens so users can't fake API calls
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-please")

# Admin Telegram user IDs (comma-separated list of integers)
_admin_ids = os.getenv("ADMIN_IDS", "").strip()
if _admin_ids:
    ADMIN_IDS = {int(x) for x in _admin_ids.split(",") if x.strip().isdigit()}
else:
    ADMIN_IDS = set()

# Coin ↔ INR conversion (configurable) – *NOT* an actual payment rate!
COIN_TO_INR = float(os.getenv("COIN_TO_INR", "0.10"))  # 1 coin = ₹0.10 default

# Reward per completed ad view *default* (campaigns can override)
DEFAULT_AD_REWARD = int(os.getenv("DEFAULT_AD_REWARD", 5))

# Anti-fraud controls
DAILY_AD_WATCH_LIMIT = int(os.getenv("DAILY_AD_WATCH_LIMIT", 20))
AD_COOLDOWN_SECONDS = int(os.getenv("AD_COOLDOWN_SECONDS", 60))  # min gap between same campaign

# Withdrawal constraints
MIN_WITHDRAW_COINS = int(os.getenv("MIN_WITHDRAW_COINS", 500))
WITHDRAW_BATCH_REVIEW_HOURS = int(os.getenv("WITHDRAW_BATCH_REVIEW_HOURS", 24))

# Language settings
# auto|en|hi  → auto = detect from user language_code; fallback en
LANG_MODE = os.getenv("LANG_MODE", "auto").lower()

# Force join (optional) – require user to join these channels before earning
# Comma-separated @usernames (without https://t.me/)
_force_join = os.getenv("FORCE_JOIN_CHANNELS", "").strip()
FORCE_JOIN_CHANNELS = [x.strip().lstrip("@") for x in _force_join.split(",") if x.strip()]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class Config:
    api_id = API_ID
    api_hash = API_HASH
    bot_token = BOT_TOKEN
    mongo_uri = MONGO_URI
    mongo_db = MONGO_DB_NAME
    base_url = BASE_URL
    secret_key = SECRET_KEY
    admin_ids = ADMIN_IDS
    coin_to_inr = COIN_TO_INR
    default_ad_reward = DEFAULT_AD_REWARD
    daily_ad_watch_limit = DAILY_AD_WATCH_LIMIT
    ad_cooldown_seconds = AD_COOLDOWN_SECONDS
    min_withdraw_coins = MIN_WITHDRAW_COINS
    withdraw_batch_review_hours = WITHDRAW_BATCH_REVIEW_HOURS
    lang_mode = LANG_MODE
    force_join_channels = FORCE_JOIN_CHANNELS
    log_level = LOG_LEVEL

CONFIG = Config()


---
