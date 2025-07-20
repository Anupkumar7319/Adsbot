"""Central bilingual message strings.
Add/modify translations easily.
"""
from config import CONFIG

# English strings
EN = {
    'welcome': "👋 Welcome! Use /earn to watch ads and earn coins.",
    'force_join': "Please join the required channel(s) before earning:",
    'joined_check': "Tap after joining:",
    'earn_button': "Watch Ad & Earn",
    'no_ads': "No ads available right now. Please try again later.",
    'balance': "💰 Your balance: {coins} coins (~₹{inr})",
    'daily_limit': "You've reached today's watch limit. Come back tomorrow!",
    'cooldown': "Please wait {secs}s before watching this ad again.",
    'watch_ack': "Ad completed! You earned {coins} coins.",
    'withdraw_usage': "Usage: /withdraw <coins> <UPI_ID>\nExample: /withdraw 500 user@upi",
    'withdraw_min': "Minimum withdrawal is {minc} coins.",
    'withdraw_not_enough': "You don't have that many coins.",
    'withdraw_ok': "Withdrawal requested: {coins} coins (~₹{inr}). We'll review soon.",
    'admin_only': "This command is for admins only.",
    'ad_added': "Ad added with id: {ad_id}",
    'ad_activated': "Ad activated.",
    'ad_deactivated': "Ad deactivated.",
    'stats_head': "📊 Stats",
    'withdraw_list_head': "Pending withdrawals:",
}

# Hindi strings (simple conversational tone)
HI = {
    'welcome': "👋 स्वागत है! /earn दबाकर विज्ञापन देखो और कॉइन कमाओ।",
    'force_join': "कमाने से पहले इन चैनल्स को जॉइन करें:",
    'joined_check': "जॉइन करने के बाद टैप करें:",
    'earn_button': "Ad Dekho, Coin Kamao",
    'no_ads': "अभी कोई विज्ञापन उपलब्ध नहीं है। बाद में कोशिश करें।",
    'balance': "💰 आपका बैलेंस: {coins} कॉइन (लगभग ₹{inr})",
    'daily_limit': "आज का लिमिट पूरा हो गया। कल दोबारा आएं!",
    'cooldown': "कृपया {secs} सेकंड रुकें फिर ये विज्ञापन देखें।",
    'watch_ack': "Ad पूरा देखा! आपको {coins} कॉइन मिले।",
    'withdraw_usage': "ऐसे करें: /withdraw <कॉइन> <UPI_ID>\nउदाहरण: /withdraw 500 user@upi",
    'withdraw_min': "कम से कम {minc} कॉइन चाहिए।",
    'withdraw_not_enough': "आपके पास इतने कॉइन नहीं हैं।",
    'withdraw_ok': "निकासी रिक्वेस्ट भेजी गई: {coins} कॉइन (~₹{inr}). हम जल्दी प्रोसेस करेंगे।",
    'admin_only': "यह कमांड सिर्फ एडमिन के लिए है।",
    'ad_added': "Ad add हो गया: {ad_id}",
    'ad_activated': "Ad चालू किया गया।",
    'ad_deactivated': "Ad बंद किया गया।",
    'stats_head': "📊 आँकड़े",
    'withdraw_list_head': "पेंडिंग निकासी:",
}


LANG_MAP = {'en': EN, 'hi': HI}


def pick_lang(user_lang_code: str = None):
    """Return language dict based on CONFIG.lang_mode & user preference."""
    if CONFIG.lang_mode == 'en':
        return EN
    if CONFIG.lang_mode == 'hi':
        return HI
    # auto
    if user_lang_code and user_lang_code.lower().startswith('hi'):
        return HI
    return EN


---
