"""Entry point: start both Flask web app and Pyrogram bot.
On Render (single web service) we run Flask, and start bot in background async task.
"""
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters

from config import CONFIG
from web_routes import web_bp
from bot_handlers import (
    start_handler, fjchk_cb, balance_handler, earn_handler, earnlist_handler,
    withdraw_handler, adsadmin_handler, addad_handler, disablead_handler,
    enablead_handler, list_withdraw_handler, pay_handler, reject_handler
)

app = Flask(__name__)
app.register_blueprint(web_bp)

# Create Pyrogram Client
bot = Client(
    name="watch_ads_earn_bot",
    api_id=CONFIG.api_id,
    api_hash=CONFIG.api_hash,
    bot_token=CONFIG.bot_token,
    in_memory=True,
)

# --- Register Handlers ---
@bot.on_message(filters.command("start"))
async def _start(c, m):
    await start_handler(c, m)

@bot.on_callback_query(filters.regex("^fjchk$"))
async def _fjchk(c, q):
    await fjchk_cb(c, q)

@bot.on_message(filters.command("balance"))
async def _bal(c, m):
    await balance_handler(c, m)

@bot.on_message(filters.command("earn"))
async def _earn(c, m):
    await earn_handler(c, m)

@bot.on_message(filters.command("earnlist"))
async def _earnlist(c, m):
    await earnlist_handler(c, m)

@bot.on_message(filters.command("withdraw"))
async def _wd(c, m):
    await withdraw_handler(c, m)

@bot.on_message(filters.command("adsadmin"))
async def _adsadmin(c, m):
    await adsadmin_handler(c, m)

@bot.on_message(filters.command("addad"))
async def _addad(c, m):
    await addad_handler(c, m)

@bot.on_message(filters.command("disablead"))
async def _disablead(c, m):
    await disablead_handler(c, m)

@bot.on_message(filters.command("enablead"))
async def _enablead(c, m):
    await enablead_handler(c, m)

@bot.on_message(filters.command("listwithdraw"))
async def _lw(c, m):
    await list_withdraw_handler(c, m)

@bot.on_message(filters.command("pay"))
async def _pay(c, m):
    await pay_handler(c, m)

@bot.on_message(filters.command("reject"))
async def _rej(c, m):
    await reject_handler(c, m)


# --- Run bot in background thread ---

def run_bot():
    bot.run()


def start_bot_in_thread():
    t = threading.Thread(target=run_bot, name="pyrogram-bot", daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    start_bot_in_thread()
    # Start Flask (blocking)
    app.run(host="0.0.0.0", port=5000)


---
