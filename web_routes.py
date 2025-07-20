"""Flask routes for ad rendering & reward callback."""
from flask import Blueprint, request, render_template, abort, jsonify
from bson import ObjectId
from config import CONFIG
from models import get_ad, mark_impression_completed, reward_impression, last_completed_for_campaign
from models import get_user, get_today_watch_count, record_impression
from security import sign_reward_token, verify_reward_token

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def home():
    return "OK - Watch Ads & Earn Bot backend running"


@web_bp.route('/watch/<int:user_id>/<ad_id>')
def watch_ad(user_id, ad_id):
    # Validate ad exists & active
    ad = get_ad(ad_id)
    if not ad or not ad.get('active', False):
        abort(404)

    # Create impression at open time
    impression_id = record_impression(user_id, ad_id)

    # Sign token for JS credit callback
    token = sign_reward_token(user_id, ad_id, impression_id)

    return render_template(
        'ad_page.html',
        title=ad.get('title', 'Ad'),
        ad=ad,
        user_id=user_id,
        token=token,
    )


@web_bp.route('/api/credit', methods=['POST'])
def api_credit():
    data = request.json or {}
    token = data.get('token')
    progress = float(data.get('progress', 0))  # 0-1 video completion

    tup = verify_reward_token(token)
    if not tup:
        return jsonify({'ok': False, 'error': 'bad_token'}), 400
    user_id, campaign_id, impression_id = tup

    ad = get_ad(campaign_id)
    if not ad:
        return jsonify({'ok': False, 'error': 'ad_missing'}), 404

    # Has user hit daily limit?
    if get_today_watch_count(user_id) >= CONFIG.daily_ad_watch_limit:
        return jsonify({'ok': False, 'error': 'daily_limit'}), 403

    # Per-campaign cooldown
    last = last_completed_for_campaign(user_id, campaign_id)
    if last and last.get('completed_at'):
        from datetime import datetime, timezone
        cooldown = ad.get('cooldown_seconds', CONFIG.ad_cooldown_seconds)
        if (datetime.now(timezone.utc) - last['completed_at']).total_seconds() < cooldown:
            return jsonify({'ok': False, 'error': 'cooldown'}), 403

    # Require at least 80% progress to credit
    if progress < 0.8:
        return jsonify({'ok': False, 'error': 'not_complete'}), 400

    # Mark & reward
    mark_impression_completed(impression_id)
    reward_impression(impression_id, user_id, ad.get('reward_coins'))
    return jsonify({'ok': True, 'reward': ad.get('reward_coins')})


---
