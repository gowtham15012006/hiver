"""
Hybrid RAG Knowledge Base Retriever for Historical Resolutions and Apple Support Policies.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from agent.config import APPLE_RESOURCES

class KnowledgeRetriever:
    """
    RAG Retriever that indexes historical Twitter resolutions and official
    Apple Support documentation to ground agent responses.
    """
    def __init__(self, kb_path: str = "data/knowledge_base/resolutions.json"):
        self.kb_path = kb_path
        self.corpus: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=10000,
            sublinear_tf=True
        )
        self._load_and_index_corpus()

    def _load_and_index_corpus(self):
        """Load historical resolutions and add structured policy documents."""
        # 1. Official Knowledge Policy Base Articles
        policy_articles = [
            {
                "id": "KB_POLICY_REPAIR",
                "title": "Hardware Repair & Genius Bar Appointments",
                "content": "For physical damage, cracked screens, battery replacements, or water damage, direct users to schedule an appointment at an Apple Store Genius Bar or Apple Authorized Service Provider via https://support.apple.com/repair. Warn against charging wet devices.",
                "url": APPLE_RESOURCES["repair"]
            },
            {
                "id": "KB_POLICY_SECURITY",
                "title": "Apple ID Security and Account Recovery",
                "content": "Strict security policy: Never ask for or accept Apple ID passwords, 2FA verification codes, or personal credentials over social media or DM. Direct users to self-serve identity recovery at https://iforgot.apple.com and https://appleid.apple.com.",
                "url": APPLE_RESOURCES["iforgot"]
            },
            {
                "id": "KB_POLICY_BILLING",
                "title": "App Store Invoices, Subscriptions & Refunds",
                "content": "To dispute unauthorized charges or request refunds for accidental subscription renewals or child in-app purchases, guide users to sign in at https://reportaproblem.apple.com. Subscriptions can be managed directly on iPhone via Settings > Apple ID > Subscriptions.",
                "url": APPLE_RESOURCES["report_problem"]
            },
            {
                "id": "KB_POLICY_SETUP",
                "title": "Device Setup, Quick Start & Pairing",
                "content": "For migrating from Android to iPhone, use the 'Move to iOS' app from Google Play. For iPhone-to-iPhone migration, power on the new device and place it near the old device to trigger Quick Start. For Apple Watch pairing, open the Apple Watch app on iPhone and tap Start Pairing.",
                "url": "https://support.apple.com/HT201196"
            },
            {
                "id": "KB_POLICY_TROUBLESHOOTING",
                "title": "iOS & macOS Glitch Troubleshooting Protocol",
                "content": "For freezes, keyboard lag, or battery drain: 1) Verify iOS version under Settings > General > About; 2) Perform force restart; 3) Check storage space under Settings > General > iPhone Storage; 4) Check battery usage per app in Settings > Battery.",
                "url": APPLE_RESOURCES["contact"]
            },
            {
                "id": "KB_POLICY_ORDERS",
                "title": "Apple Store Online Orders & Trade-in Tracking",
                "content": "Track online orders, shipment status, and trade-in kit delivery at https://www.apple.com/orderstatus using the Web Order Number (W-number). For delayed shipments or lost deliveries, escalate to support specialist via DM.",
                "url": APPLE_RESOURCES["order_status"]
            },
            {
                "id": "KB_POLICY_FEEDBACK",
                "title": "Product Feedback and Store Inquiries",
                "content": "Direct feature suggestions and operating system improvement requests to https://www.apple.com/feedback. For store operating hours and workshop schedules, direct to https://www.apple.com/retail.",
                "url": APPLE_RESOURCES["feedback"]
            }
        ]
        
        self.corpus.extend(policy_articles)

        # 2. Historical Twitter resolutions from dataset
        if os.path.exists(self.kb_path):
            try:
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    resolutions = json.load(f)
                    for r in resolutions[:1000]: # Index top 1,000 historical resolutions
                        self.corpus.append({
                            "id": r.get("id", "hist"),
                            "title": f"Historical Resolution: {r.get('customer_problem', '')[:40]}...",
                            "content": f"Customer Query: {r.get('customer_problem', '')}\nHistorical Resolution: {r.get('historical_resolution', '')}",
                            "url": APPLE_RESOURCES["contact"]
                        })
            except Exception as e:
                print(f"Notice: Could not load historical resolutions file: {e}")

        # Index corpus texts
        corpus_texts = [f"{doc.get('title', '')} {doc.get('content', '')}" for doc in self.corpus]
        self.doc_matrix = self.vectorizer.fit_transform(corpus_texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the top-k most relevant knowledge articles and historical resolutions."""
        if not query or not query.strip():
            return self.corpus[:top_k]

        cleaned = re.sub(r"@\w+", "", query).strip().lower()
        q_vec = self.vectorizer.transform([cleaned])
        sims = cosine_similarity(q_vec, self.doc_matrix)[0]

        top_indices = sims.argsort()[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(sims[idx])
            doc = self.corpus[idx].copy()
            doc["retrieval_score"] = round(score, 4)
            results.append(doc)
            
        return results
