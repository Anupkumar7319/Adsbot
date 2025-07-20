"""All Telegram bot handlers (Pyrogram)."""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CONFIG
from models import (
    get_or_create_user, get_user, get_active_ads, get_ad, set_ad_active,
    create_ad, create_withdrawal, get_today_watch_count, deduct_coins,
    list_withdrawals, update_withdrawal_status
)
from messages import pick_lang
from utils import coins_to_inr, parse_withdraw_args


# --------------
# Force Join Check
# --------------
async def _user_in_required_channels(app: Client, user_id: int) -> bool:
    if not CONFIG.force_join_channels:
        return True
    for chan in CONFIG.force_join_channels:
        try:
            member = await app.get_chat_member(chan, user_id)
            if member.status in ("kicked", "left"):
                return False
        except Exception:
            return False
    return True


def _force_join_markup():
    rows = []
    for chan in CONFIG.force_join_channels:
        rows.append([InlineKeyboardButton(f"@{chan}", url=f"https://t.me/{chan}")])
    rows.append([InlineKeyboardButton("Joined ✅", callback_data="fjchk")])
    return InlineKeyboardMarkup(rows)


# --------------
# /start
# --------------
async def start_handler(app: Client, message):
    user = get_or_create_user(message.from_user.id, username=message.from_user.username, lang=message.from_user.language_code)
    lang = pick_lang(user.get('lang'))

    if not await _user_in_required_channels(app, message.from_user.id):
        await message.reply(lang['force_join'], reply_markup=_force_join_markup())
        return

    coins = user.get('coins', 0)
    await message.reply(lang['welcome'] + "\n" + lang['balance'].format(coins=coins, inr=coins_to_inr(coins)))


# --------------
# Force Join Callback
# --------------
async def fjchk_cb(app: Client, callback_query):
    user_id = callback_query.from_user.id
    user = get_user(user_id) or get_or_create_user(user_id)
    lang = pick_lang(user.get('lang'))

    if not await _user_in_required_channels(app, user_id):
        await callback_query.answer("Still not joined.", show_alert=True)
        return
    await callback_query.message.edit_text(lang['welcome'])


# --------------
# /balance
# --------------
async def balance_handler(app: Client, message):
    user = get_user(message.from_user.id)
    if not user:
        user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
    lang = pick_lang(user.get('lang'))
    coins = user.get('coins', 0)
    await message.reply(lang['balance'].format(coins=coins, inr=coins_to_inr(coins)))


# --------------
# /earn – show one (first) active ad, with button to watch
# --------------
async def earn_handler(app: Client, message):
    user = get_user(message.from_user.id) or get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
    lang = pick_lang(user.get('lang'))

    if not await _user_in_required_channels(app, message.from_user.id):
        await message.reply(lang['force_join'], reply_markup=_force_join_markup())
        return

    if get_today_watch_count(message.from_user.id) >= CONFIG.daily_ad_watch_limit:
        await message.reply(lang['daily_limit'])
        return

    ads = get_active_ads()
    if not ads:
        await message.reply(lang['no_ads'])
        return

    ad = ads[0]
    url = f"{CONFIG.base_url}/watch/{message.from_user.id}/{ad['_id']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(lang['earn_button'], url=url)]])
    await message.reply(f"{ad['title']}\nReward: {ad.get('reward_coins')} coins", reply_markup=kb)


# --------------
# /earnlist – show multiple ads
# --------------
async def earnlist_handler(app: Client, message):
    user = get_user(message.from_user.id) or get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
    lang = pick_lang(user.get('lang'))
    ads = get_active_ads()
    if not ads:
        await message.reply(lang['no_ads'])
        return
    rows = []
    for ad in ads:
        url = f"{CONFIG.base_url}/watch/{message.from_user.id}/{ad['_id']}"
        rows.append([InlineKeyboardButton(f"{ad['title']} (+{ad.get('reward_coins')}c)", url=url)])
    await message.reply(lang['earn_button'], reply_markup=InlineKeyboardMarkup(rows))


# --------------
# /withdraw <coins> <UPI>
# --------------
async def withdraw_handler(app: Client, message):
    user = get_user(message.from_user.id) or get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
    lang = pick_lang(user.get('lang'))

    amt, upi = parse_withdraw_args(message.text)
    if not amt or not upi:
        await message.reply(lang['withdraw_usage'])
        return
    if amt < CONFIG.min_withdraw_coins:
        await message.reply(lang['withdraw_min'].format(minc=CONFIG.min_withdraw_coins))
        return
    if user.get('coins', 0) < amt:
        await message.reply(lang['withdraw_not_enough'])
        return

    if not deduct_coins(user['_id'], amt):
        await message.reply(lang['withdraw_not_enough'])
        return

    wid = create_withdrawal(user['_id'], amt, upi)
    await message.reply(lang['withdraw_ok'].format(coins=amt, inr=amt * CONFIG.coin_to_inr))

    # Notify admins
    for admin_id in CONFIG.admin_ids:
        try:
            await app.send_message(admin_id, f"New withdrawal request {wid} from {user['_id']} {amt} coins ({amt * CONFIG.coin_to_inr} INR) UPI: {upi}")
        except Exception:
            pass


# -----------------
# ADMIN COMMANDS
# -----------------
async def _is_admin(user_id: int) -> bool:
    return user_id in CONFIG.admin_ids


async def adsadmin_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    ads = get_active_ads()
    txt = "Active Ads:\n" + "\n".join([f"{a['_id']} - {a['title']} ({a.get('reward_coins')}c)" for a in ads])
    txt += "\n\nAdd ad: /addad <title>|<reward>|<video_url>"
    await message.reply(txt)


async def addad_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    # Parse simple pipe format
    try:
        _, rest = message.text.split(' ', 1)
        title, reward, video_url = rest.split('|', 2)
        reward = int(reward)
    except Exception:
        await message.reply("Usage: /addad title|reward|video_url")
        return
    ad_id = create_ad(title=title.strip(), ad_type='video', reward_coins=reward, video_url=video_url.strip(), landing_url=None)
    await message.reply(f"Ad created: {ad_id}")


async def disablead_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Usage: /disablead <id>")
        return
    set_ad_active(parts[1], False)
    await message.reply("Ad disabled.")


async def enablead_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Usage: /enablead <id>")
        return
    set_ad_active(parts[1], True)
    await message.reply("Ad enabled.")


async def list_withdraw_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    pend = list_withdrawals(status='pending', limit=50)
    if not pend:
        await message.reply("No pending withdrawals.")
        return
    lines = []
    for w in pend:
        lines.append(f"{w['_id']} user:{w['user_id']} {w['amount_coins']}c ({w['amount_inr']} INR) UPI:{w['upi_id']}")
    await message.reply("\n".join(lines) + "\n\nPay: /pay <id> | Reject: /reject <id>")


async def pay_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Usage: /pay <withdraw_id>")
        return
    wid = parts[1]
    update_withdrawal_status(wid, 'paid')
    await message.reply(f"Marked paid: {wid}")


async def reject_handler(app: Client, message):
    if not await _is_admin(message.from_user.id):
        await message.reply("Not admin.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Usage: /reject <withdraw_id>")
        return
    wid = parts[1]
    update_withdrawal_status(wid, 'rejected')
    await message.reply(f"Rejected: {wid}")


---
