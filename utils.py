"""Utility helpers."""
from config import CONFIG


def coins_to_inr(coins: int) -> float:
    return round(coins * CONFIG.coin_to_inr, 2)


def parse_withdraw_args(text: str):
    """Parse '/withdraw 500 user@upi' -> (500, 'user@upi')"""
    parts = text.strip().split()
    if len(parts) < 3:
        return None, None
    try:
        amt = int(parts[1])
    except ValueError:
        return None, None
    upi = parts[2]
    return amt, upi


---
