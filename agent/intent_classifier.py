"""
Semantic and Few-Shot Intent Classifier for Apple Support Agent.
Implements calibrated multi-intent classification across the 7 domain intents.
"""

import os
import re
import math
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from agent.taxonomy import INTENT_TAXONOMY, ALL_INTENTS

class IntentClassifier:
    """
    Robust, calibrated Intent Classifier combining TF-IDF N-gram semantic matching
    with prototypical few-shot intent representations and context-aware boundary disambiguation.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            stop_words="english",
            sublinear_tf=True,
            max_features=6000
        )
        self._build_intent_prototypes()

    def _build_intent_prototypes(self):
        """Build prototype documents for each intent from taxonomy definitions and examples."""
        self.intent_documents = []
        self.intent_labels = []
        
        for intent_name, intent_def in INTENT_TAXONOMY.items():
            # Combine description, boundary notes, and prototypical examples
            text_corpus = " ".join([
                intent_def.description,
                intent_def.decision_boundary_note,
                " ".join(intent_def.prototypical_examples) * 3
            ])
            self.intent_documents.append(text_corpus)
            self.intent_labels.append(intent_name)
            
        self.prototype_matrix = self.vectorizer.fit_transform(self.intent_documents)

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify input text into one of the 7 taxonomy intents with confidence scores.
        """
        if not text or not text.strip():
            return {
                "predicted_intent": "GENERAL_INQUIRY_FEEDBACK",
                "confidence": 0.30,
                "all_scores": {k: 0.14 for k in ALL_INTENTS},
                "is_low_confidence": True
            }

        cleaned = re.sub(r"@\w+", "", text).strip().lower()
        query_vec = self.vectorizer.transform([cleaned])
        sims = cosine_similarity(query_vec, self.prototype_matrix)[0]

        score_dict = {self.intent_labels[i]: float(sims[i]) for i in range(len(self.intent_labels))}

        # Helper for whole-word search
        def has_any(keywords):
            return any(re.search(r"\b" + re.escape(w) + r"\b", cleaned) for w in keywords)

        # 1. HARDWARE_PHYSICAL_DAMAGE
        if has_any(["crack", "cracked", "shatter", "shattered", "spill", "spilled", "water damage", "pool", "toilet", "swollen battery", "battery swollen", "smoke", "bent chassis", "snapped", "broken port", "broken glass", "submerged"]):
            score_dict["HARDWARE_PHYSICAL_DAMAGE"] += 0.35
        elif "screen" in cleaned and has_any(["drop", "dropped", "hit", "smashed", "black spot"]):
            score_dict["HARDWARE_PHYSICAL_DAMAGE"] += 0.35

        # Explicit negation for physical damage
        if has_any(["not physical", "not physical damage", "no physical damage", "didn't drop", "never dropped", "without dropping", "not dropped"]):
            score_dict["HARDWARE_PHYSICAL_DAMAGE"] = max(0.0, score_dict["HARDWARE_PHYSICAL_DAMAGE"] - 0.40)
            score_dict["SOFTWARE_OS_GLITCH"] += 0.35

        # 2. ACCOUNT_SECURITY_ICLOUD
        if has_any(["apple id", "icloud login", "locked account", "locked out", "iforgot", "2fa", "two-factor", "verification code", "hacked", "compromised", "activation lock", "security question"]):
            score_dict["ACCOUNT_SECURITY_ICLOUD"] += 0.35

        # 3. BILLING_SUBSCRIPTION_REFUND
        if has_any(["charged", "refund", "subscription", "cancel", "tinder", "roblox", "card declined", "billing problem", "unauthorized charge", "double charge", "stole", "invoice", "gift card"]):
            score_dict["BILLING_SUBSCRIPTION_REFUND"] += 0.35
        elif re.search(r"\$\d+", cleaned):
            score_dict["BILLING_SUBSCRIPTION_REFUND"] += 0.25

        # 4. WARRANTY_ORDER_SHIPPING
        if has_any(["order status", "ups", "fedex", "shipment", "delivery", "trade-in", "trade in", "repair id", "checkcoverage", "applecare status", "tracking number", "preparing for shipment"]):
            score_dict["WARRANTY_ORDER_SHIPPING"] += 0.35

        # 5. DEVICE_SETUP_COMPATIBILITY
        if has_any(["how do i set up", "how to set up", "how do i pair", "quick start", "move to ios", "pair apple watch", "airdrop settings", "family sharing", "how do i transfer", "connect airpods"]):
            score_dict["DEVICE_SETUP_COMPATIBILITY"] += 0.35

        # 6. GENERAL_INQUIRY_FEEDBACK & Greetings / Identity
        if has_any(["store hours", "retail store", "recycling", "today at apple", "rumor", "feedback", "feature suggestion", "covent garden", "5th avenue", "compliment", "who are you", "your name", "what is your name", "who am i talking to", "what are you", "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "what can you do"]):
            score_dict["GENERAL_INQUIRY_FEEDBACK"] += 0.45

        # 7. SOFTWARE_OS_GLITCH
        if has_any(["freeze", "frozen", "lag", "slow", "boot loop", "kernel panic", "battery drain", "battery health", "battery drop", "warm", "autocorrect", "bluetooth unpair", "wifi disconnect", "not loading", "crash", "glitch", "apple logo", "after update", "os update", "ios update", "software update", "system update", "during update", "green line", "pink line", "vertical line", "screen line", "flicker", "flickering", "display issue", "screen issue"]):
            score_dict["SOFTWARE_OS_GLITCH"] += 0.40

        # Disambiguate ultra-vague queries
        if len(cleaned.split()) <= 4 and "help" in cleaned:
            score_dict["GENERAL_INQUIRY_FEEDBACK"] += 0.20

        # Softmax normalization with temperature scaling
        scores_list = [max(0.0, score_dict[intent]) for intent in ALL_INTENTS]
        total_exp = sum(math.exp(s * 8.0) for s in scores_list)
        prob_dict = {intent: math.exp(score_dict[intent] * 8.0) / total_exp for intent in ALL_INTENTS}

        sorted_intents = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_conf = sorted_intents[0]

        return {
            "predicted_intent": top_intent,
            "confidence": round(top_conf, 4),
            "all_scores": {k: round(v, 4) for k, v in prob_dict.items()},
            "is_low_confidence": top_conf < 0.30
        }
