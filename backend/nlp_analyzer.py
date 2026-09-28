"""
nlp_analyzer.py
Simple keyword + context based scam call transcript analyzer.
No heavy NLP model needed — keyword scoring is fast and explainable.
"""

import re

# Keywords grouped by how strongly they signal a scam, with weights
HIGH_RISK_KEYWORDS = {
    "otp": 5,
    "one time password": 5,
    "password": 4,
    "cvv": 5,
    "card number": 5,
    "pin number": 5,
    "social security": 4,
    "verify your account": 4,
    "wire transfer": 4,
    "gift card": 4,
    "urgent": 2,
    "act now": 3,
    "suspended": 3,
    "bank account": 2,
    "refund": 2,
    "irs": 3,
    "arrest warrant": 5,
    "lottery": 4,
    "you have won": 4,
    "remote access": 4,
    "install this app": 4,
    "confidential": 2,
}

SAFE_CONTEXT_HINTS = {
    "customer support ticket": -2,
    "appointment reminder": -3,
    "delivery scheduled": -2,
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def analyze_call(transcript: str) -> dict:
    text = clean_text(transcript)

    matched_keywords = []
    score = 0

    for phrase, weight in HIGH_RISK_KEYWORDS.items():
        if phrase in text:
            score += weight
            matched_keywords.append(phrase)

    for phrase, weight in SAFE_CONTEXT_HINTS.items():
        if phrase in text:
            score += weight  # negative weight lowers the score

    score = max(0, score)

    if score >= 10:
        verdict = "Scam"
    elif score >= 4:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    return {
        "verdict": verdict,
        "risk_score": score,
        "matched_keywords": matched_keywords,
    }


def combine_verdicts(call_result: dict, number_result: dict | None) -> dict:
    """Combine the call analysis with a phone number spam check, if provided."""
    final_score = call_result["risk_score"]

    if number_result and number_result.get("is_spam"):
        final_score += 6

    if final_score >= 10:
        final_verdict = "Scam"
    elif final_score >= 4:
        final_verdict = "Suspicious"
    else:
        final_verdict = "Safe"

    return {
        "final_verdict": final_verdict,
        "final_score": final_score,
        "call_analysis": call_result,
        "number_check": number_result,
    }
