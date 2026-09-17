"""
Trivial Baseline: Naive Keyword Matching + Static Canned Reply + Naive Length Escalation.
Serves as the lower-bound reference baseline.
"""

import time
from typing import Dict, List, Any, Optional

from agent.taxonomy import ALL_INTENTS

class TrivialBaseline:
    """
    Trivial baseline implementing naive keyword search and static canned replies.
    """
    def __init__(self):
        self.name = "Baseline 1 (Trivial Heuristic)"

    def process_message(self, customer_text: str, context: Optional[str] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        text_lower = customer_text.lower()

        # Naive keyword matching
        if "screen" in text_lower or "drop" in text_lower:
            intent = "HARDWARE_PHYSICAL_DAMAGE"
        elif "password" in text_lower or "account" in text_lower:
            intent = "ACCOUNT_SECURITY_ICLOUD"
        elif "refund" in text_lower or "bill" in text_lower or "charge" in text_lower:
            intent = "BILLING_SUBSCRIPTION_REFUND"
        elif "setup" in text_lower or "pair" in text_lower:
            intent = "DEVICE_SETUP_COMPATIBILITY"
        elif "order" in text_lower or "shipping" in text_lower:
            intent = "WARRANTY_ORDER_SHIPPING"
        elif "store" in text_lower or "hours" in text_lower:
            intent = "GENERAL_INQUIRY_FEEDBACK"
        else:
            # Default to majority intent
            intent = "SOFTWARE_OS_GLITCH"

        # Naive escalation decision: escalate only if text length > 100 characters
        if len(customer_text) > 100:
            decision = "ESCALATE_TO_HUMAN"
            reason = "message_too_long"
        else:
            decision = "AUTO_HANDLE"
            reason = None

        # Static canned reply
        canned_reply = "Thank you for contacting Apple Support. Please restart your device. If the issue persists, visit support.apple.com."

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "customer_query": customer_text,
            "predicted_intent": intent,
            "intent_confidence": 0.50,
            "decision": decision,
            "escalation_reason": reason,
            "draft_reply": canned_reply,
            "grounding_citations": ["https://support.apple.com"],
            "grounding_source": "CANNOT_RETRIEVE_TRIVIAL",
            "latency_ms": latency_ms
        }
