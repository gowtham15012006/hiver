"""
Configuration, Brand Guidelines, and Escalation Rules for Apple Support AI Agent.
"""

import os
from typing import Dict, List, Any

# Brand Identity
BRAND_NAME = "AppleSupport"
BRAND_VOICE = "Helpful, empathetic, professional, clear, and proactive. Use concise language typical of Apple customer care."

# Official Apple Support resource links
APPLE_RESOURCES = {
    "repair": "https://support.apple.com/repair",
    "iforgot": "https://iforgot.apple.com",
    "report_problem": "https://reportaproblem.apple.com",
    "order_status": "https://www.apple.com/orderstatus",
    "check_coverage": "https://checkcoverage.apple.com",
    "retail_stores": "https://www.apple.com/retail",
    "feedback": "https://www.apple.com/feedback",
    "contact": "https://support.apple.com/contact"
}

# Mandatory Escalation Triggers
ESCALATION_RULES = {
    "HARDWARE_SAFETY_OR_DAMAGE": {
        "description": "Physical damage (cracked screen, water damage, swelling battery, smoking/sparking).",
        "reason": "requires_hardware_inspection_or_genius_bar",
        "decision": "ESCALATE_TO_HUMAN"
    },
    "ACCOUNT_SECURITY_LOCKOUT": {
        "description": "Locked Apple ID, forgotten password, 2FA issues, hacked/compromised account.",
        "reason": "security_sensitive_credentials_or_account_lockout",
        "decision": "ESCALATE_TO_HUMAN"
    },
    "FINANCIAL_OR_BILLING_DISPUTE": {
        "description": "Refund requests, unauthorized charges, subscription dispute.",
        "reason": "financial_transaction_and_refund_authorization",
        "decision": "ESCALATE_TO_HUMAN"
    },
    "ORDER_OR_WARRANTY_LOOKUP": {
        "description": "Shipping delay, lost delivery, trade-in kit delay, repair ID status tracking.",
        "reason": "order_logistics_or_warranty_system_lookup",
        "decision": "ESCALATE_TO_HUMAN"
    },
    "HIGH_FRUSTRATION_OR_LEGAL": {
        "description": "Severe customer anger, profanity, threats of legal action or consumer protection complaint.",
        "reason": "high_customer_frustration_or_legal_escalation",
        "decision": "ESCALATE_TO_HUMAN"
    },
    "REPEATED_FAILURE_AFTER_TROUBLESHOOTING": {
        "description": "Customer indicates they already restarted/restored/tried all standard steps without success.",
        "reason": "unresolved_after_standard_troubleshooting",
        "decision": "ESCALATE_TO_HUMAN"
    }
}

# Negative sentiment & escalation keywords
ANGER_LEGAL_KEYWORDS = [
    "sue", "lawsuit", "lawyer", "attorney", "legal action", "court",
    "scam", "fraud", "thieves", "stealing", "robbery", "unacceptable",
    "worst service", "useless", "furious", "garbage", "trash", "disgusted",
    "ripoff", "rip off", "bbb", "consumer protection", "ftc"
]

REPEATED_FAILURE_KEYWORDS = [
    "already tried", "already restarted", "already reset", "still not working",
    "nothing worked", "did that already", "done that", "still happening",
    "fourth time", "third time", "didn't help", "does not help"
]
