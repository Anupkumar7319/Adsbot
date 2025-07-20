"""Security helpers: sign/verify reward tokens so users can't spoof rewards."""
import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Tuple
from config import CONFIG


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def _b64d(data: str) -> bytes:
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def sign_reward_token(user_id: int, campaign_id: str, impression_id: str, ttl_seconds: int = 600) -> str:
    payload = {
        'u': user_id,
        'c': campaign_id,
        'i': impression_id,
        'exp': int(time.time()) + ttl_seconds,
    }
    raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()
    sig = hmac.new(CONFIG.secret_key.encode(), raw, hashlib.sha256).digest()
    return _b64(raw) + '.' + _b64(sig)


def verify_reward_token(token: str) -> Optional[Tuple[int, str, str]]:
    try:
        raw_b64, sig_b64 = token.split('.')
    except ValueError:
        return None
    raw = _b64d(raw_b64)
    expected_sig = hmac.new(CONFIG.secret_key.encode(), raw, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64d(sig_b64)):
        return None
    import json, time
    payload = json.loads(raw)
    if payload.get('exp', 0) < time.time():
        return None
    return payload['u'], payload['c'], payload['i']


---
