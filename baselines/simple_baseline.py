"""
Simple Baseline: Generic Zero-Shot LLM / Un-calibrated TF-IDF Classifier without RAG Grounding or Strict Safety Guardrails.
"""

import time
import re
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from agent.taxonomy import ALL_INTENTS

class SimpleZeroShotBaseline:
    """
    Simple baseline: standard zero-shot classifier without RAG historical context,
    without domain boundary tuning, and without explicit multi-tier escalation policies.
    """
    def __init__(self):
        self.name = "Baseline 2 (Simple Zero-Shot)"
        self.vectorizer = TfidfVectorizer(stop_words="english")
        
        # Generic intent names only (no domain definitions or few-shots)
        self.intent_labels = ALL_INTENTS
        intent_simple_texts = [
            "software glitch bug crash freeze ios update battery drain",
            "hardware physical damage broken cracked screen water liquid battery",
            "account security icloud password apple id login locked 2fa",
            "billing subscription refund purchase charge invoice credit card payment",
            "device setup compatibility pairing transfer airdrop watch setup",
            "warranty order shipping delivery tracking carrier status repair",
            "general inquiry feedback store hours compliment suggest"
        ]
        self.prototype_matrix = self.vectorizer.fit_transform(intent_simple_texts)

    def process_message(self, customer_text: str, context: Optional[str] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        cleaned = re.sub(r"@\w+", "", customer_text).strip().lower()
        
        # Zero-shot classification
        q_vec = self.vectorizer.transform([cleaned])
        sims = cosine_similarity(q_vec, self.prototype_matrix)[0]
        top_idx = int(sims.argmax())
        intent = self.intent_labels[top_idx]
        confidence = float(sims[top_idx])

        # Simple un-calibrated escalation rule: only escalate if intent is HARDWARE or ACCOUNT
        if intent in ["HARDWARE_PHYSICAL_DAMAGE", "ACCOUNT_SECURITY_ICLOUD"]:
            decision = "ESCALATE_TO_HUMAN"
            reason = "general_human_escalation"
        else:
            decision = "AUTO_HANDLE"
            reason = None

        # Generic ungrounded reply generation without RAG or official Apple URLs
        reply_templates = {
            "SOFTWARE_OS_GLITCH": "Hello, sorry you are experiencing this glitch. Please update your software to the newest version or restart your phone.",
            "HARDWARE_PHYSICAL_DAMAGE": "Hello, hardware damage requires an in-person technician. Please take your phone to a repair shop.",
            "ACCOUNT_SECURITY_ICLOUD": "Hello, please reset your password on the website to fix your account issues.",
            "BILLING_SUBSCRIPTION_REFUND": "Hello, for billing problems, please check your app store receipt or contact support.",
            "DEVICE_SETUP_COMPATIBILITY": "Hello, you can set up your device in the settings menu by following the instructions.",
            "WARRANTY_ORDER_SHIPPING": "Hello, your order or warranty can be checked on the website with your tracking number.",
            "GENERAL_INQUIRY_FEEDBACK": "Hello, thank you for contacting us. We appreciate your feedback."
        }
        draft_reply = reply_templates.get(intent, "Hello, how can we assist you today?")

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "customer_query": customer_text,
            "predicted_intent": intent,
            "intent_confidence": round(confidence, 4),
            "decision": decision,
            "escalation_reason": reason,
            "draft_reply": draft_reply,
            "grounding_citations": [],
            "grounding_source": "NONE_ZERO_SHOT",
            "latency_ms": latency_ms
        }
