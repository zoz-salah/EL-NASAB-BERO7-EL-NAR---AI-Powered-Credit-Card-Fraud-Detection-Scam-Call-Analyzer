"""
number_checker.py
Checks a phone number against a spam-detection API.

Truecaller does not offer a public self-serve API, so this module is written
against NumVerify + a generic "spam list" style API (e.g. APILayer's Spam
Number Checker, or any RapidAPI spam-lookup service). Swap SPAM_API_URL and
the request/response parsing to match whichever provider you sign up for.

Set your API key as an environment variable: SPAM_API_KEY
"""

import os
import requests

SPAM_API_KEY = os.getenv("SPAM_API_KEY", "")
SPAM_API_URL = "https://api.apilayer.com/spamscore/number"  # example provider, swap as needed

# Fallback local blocklist so the endpoint still works with zero API keys configured (for demos)
LOCAL_DEMO_BLOCKLIST = {
    "+10000000000": 0.95,
    "+201000000000": 0.9,
}


def check_number(phone_number: str) -> dict:
    phone_number = phone_number.strip()

    if not SPAM_API_KEY:
        # Demo mode: use local blocklist so the feature is testable without a paid API key
        confidence = LOCAL_DEMO_BLOCKLIST.get(phone_number, 0.05)
        return {
            "phone_number": phone_number,
            "is_spam": confidence >= 0.5,
            "confidence": confidence,
            "source": "local_demo_blocklist",
        }

    try:
        response = requests.get(
            SPAM_API_URL,
            headers={"apikey": SPAM_API_KEY},
            params={"number": phone_number},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        confidence = float(data.get("spam_score", 0))
        return {
            "phone_number": phone_number,
            "is_spam": confidence >= 0.5,
            "confidence": confidence,
            "source": "spam_api",
        }
    except requests.RequestException as e:
        return {
            "phone_number": phone_number,
            "is_spam": False,
            "confidence": 0.0,
            "source": "error",
            "error": str(e),
        }
