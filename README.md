# Watch Ads & Earn – Telegram Bot

Users watch sponsor videos (or open links) to earn coins. Coins can be withdrawn (manual UPI review). Built with **Pyrogram + Flask + MongoDB**. Deploy on Render.

---
## Features
- /start registers user
- Force join channels (optional)
- /earn shows current ad (video/link)
- Web ad page credits coins after 80% watch
- Per-user daily watch limit & cooldown
- /balance shows current coins & INR approx
- /withdraw <coins> <UPI> requests payout
- Admin commands: /adsadmin, /addad, /disablead, /enablead, /listwithdraw, /pay, /reject

---
## Quick Start (Local)
1. **Clone repo**
2. `cp .env.example .env` and fill secrets
3. `python -m venv venv && source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. `python main.py`
6. Open Telegram, send `/start` to your bot.
7. Send `/addad Test|5|https://path/to/video.mp4` from an admin account.
8. Send `/earn` from user account → tap button → watch video → earn coins.

---
## MongoDB Collections
See `models.py` for schema. Minimal fields; MongoDB flexible.

---
## Deployment (Render)
1. Push repo to GitHub.
2. Create new **Web Service** in Render, pick repo.
3. Set environment variables per `.env.example`.
4. Use start command: `python main.py`.
5. After deploy, copy Render public URL → set `BASE_URL` env → redeploy.
6. Restart service.

---
## Security Notes
- SECRET_KEY must be long random string.
- Reward token signed; prevents simple spoofing.
- Still vulnerable to video skip hacks; advanced: use DRM / timed ping.
- Rate-limit `/api/credit` behind CDN (Cloudflare) if heavy traffic.

---
## Payments / Compliance Disclaimer
This code is for **educational purposes**. Real-money reward systems must follow:
- Ad network TOS (AdMob, AppLovin, etc.)
- Government/Tax/KYC rules in your country
- Anti-fraud + anti-spam measures
- User consent & privacy compliance

---
## Extend Ideas
- Referral bonus (invite friends → coins)
- Tiered ads (high reward for longer video)
- Leaderboard
- Auto-check UPI payouts via API (Razorpay/Paytm if allowed)
- Web dashboard with charts

---
## Troubleshooting
**Bot not responding?** Check BOT_TOKEN and that it isn't running elsewhere.
**Coins not crediting?** Make sure BASE_URL correct & reachable from Telegram.
**Video not playing on mobile?** Use MP4 (H.264/AAC) over HTTPS.
**Mongo error?** Whitelist IP / use `0.0.0.0/0` temporarily (dev only).

---
## License
MIT – use, modify, share freely. Attribution appreciated.


---
