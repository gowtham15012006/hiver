"""
Unified AI Customer Support Agent Orchestrator with Comprehensive Diagnostic Explanations.
Integrates Intent Classification, RAG Knowledge Retrieval, Escalation Decision Engine,
and Multi-Dimensional Customer Tweet Analysis.
"""

import time
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from agent.intent_classifier import IntentClassifier
from agent.retriever import KnowledgeRetriever
from agent.escalation_engine import EscalationEngine, EscalationResult
from agent.reply_generator import ReplyGenerator
from agent.taxonomy import INTENT_TAXONOMY
from loguru import logger

@dataclass
class DiagnosticBreakdown:
    symptom_summary: str
    severity_level: str  # "CRITICAL_SAFETY", "HIGH_SECURITY", "HIGH_FINANCIAL", "MODERATE_FUNCTIONAL", "LOW_INQUIRY"
    detected_signals: List[str]
    intent_boundary_rationale: str
    policy_risk_assessment: str
    recommended_action_plan: List[str]
    frustration_score: int = 20  # 0 to 100
    urgency_level: str = "LOW"  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    sentiment_label: str = "Calm / Neutral"  # "Calm / Neutral", "Concerned", "Frustrated", "Highly Agitated"

@dataclass
class AgentOutput:
    customer_query: str
    predicted_intent: str
    intent_confidence: float
    decision: str  # "AUTO_HANDLE" or "ESCALATE_TO_HUMAN"
    escalation_reason: Optional[str]
    escalation_rule_triggered: Optional[str]
    decision_explanation: str
    diagnostic: DiagnosticBreakdown
    draft_reply: str
    grounding_citations: List[str]
    grounding_source: str
    latency_ms: float
    retrieved_knowledge_chunks: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

class SupportAgent:
    """
    Production-grade AI Support Agent for Apple Customer Support with deep diagnostic reasoning.
    """
    def __init__(self, use_llm: bool = True):
        self.intent_classifier = IntentClassifier()
        self.retriever = KnowledgeRetriever()
        self.escalation_engine = EscalationEngine()
        self.reply_generator = ReplyGenerator(use_llm=use_llm)

    def _generate_deep_diagnostics(
        self,
        customer_text: str,
        intent: str,
        intent_conf: float,
        decision: str,
        reason: Optional[str]
    ) -> DiagnosticBreakdown:
        """Generate comprehensive multi-dimensional analysis of the customer tweet."""
        text_lower = customer_text.lower()
        signals = []

        def has_word(words_list):
            return any(re.search(r"\b" + re.escape(w) + r"\b", text_lower) for w in words_list)

        # 1. Signal Extraction
        if has_word(["water", "pool", "toilet", "liquid", "spill", "dropped in", "submerged"]):
            signals.append("Liquid Submersion / Moisture Ingress")
        if has_word(["crack", "cracked", "shatter", "shattered", "broken screen", "broken glass", "shattered screen"]):
            signals.append("Physical Impact / Broken Glass Chassis")
        if has_word(["swollen", "battery expand", "smoke", "burning", "sparks"]):
            signals.append("Thermal Event / Battery Cell Swelling")
        if has_word(["green line", "pink line", "vertical line", "screen line", "flicker", "flickering", "screen glitch"]):
            signals.append("Display Hardware / Screen Glitch")
        if has_word(["freeze", "frozen", "lag", "slow", "stuck", "boot loop", "crash"]):
            signals.append("System Responsiveness / UI Freeze")
        if has_word(["battery drain", "battery health", "drops 40%", "drops 30%", "battery dropping"]):
            signals.append("Power Management / Rapid Battery Discharge")
        if has_word(["locked", "apple id", "password", "iforgot", "2fa", "verification code"]):
            signals.append("Identity Authentication / Account Lockout")
        if has_word(["charged", "refund", "subscription", "tinder", "roblox", "money", "$", "billing", "credit card", "apple.com/bill", "receipt"]):
            signals.append("Financial Transaction / Billing Dispute")
        if has_word(["transfer", "pair", "android", "apple watch", "airdrop", "quick start"]):
            signals.append("Device Migration / Peripheral Pairing")
        if has_word(["sue", "lawyer", "attorney", "lawsuit", "scam", "fraud", "thieves", "useless", "worst"]):
            signals.append("Customer Frustration / Legal Sensitivity")

        if not signals:
            signals.append("General Technical Inquiry / Feature Question")

        # 2. Severity Level
        if any("Swelling" in s or "Moisture" in s or "Impact" in s for s in signals):
            severity = "CRITICAL_SAFETY"
        elif any("Authentication" in s for s in signals):
            severity = "HIGH_SECURITY"
        elif any("Billing" in s or "Legal" in s for s in signals):
            severity = "HIGH_FINANCIAL"
        elif any("Freeze" in s or "Discharge" in s or "Display" in s for s in signals):
            severity = "MODERATE_FUNCTIONAL"
        else:
            severity = "LOW_INQUIRY"

        # 3. Intent Boundary Rationale
        intent_def = INTENT_TAXONOMY.get(intent)
        boundary_rationale = intent_def.decision_boundary_note if intent_def else "Standard intent boundary applied."

        # 4. Policy Risk Assessment
        if decision == "ESCALATE_TO_HUMAN":
            if reason == "requires_hardware_inspection_or_genius_bar":
                policy_risk = "High Physical Risk: Continuing device operation or applying electrical charging current to damaged/wet components creates fire and short-circuit hazards. Autonomous software troubleshooting is blocked."
            elif reason == "security_sensitive_credentials_or_account_lockout":
                policy_risk = "High Security & Compliance Risk: Apple privacy regulations strictly forbid accepting user credentials, passwords, or recovery codes on public or social channels. Directing to official cryptographic recovery portals."
            elif reason == "financial_transaction_and_refund_authorization":
                policy_risk = "Financial Audit Risk: Refund issuance and chargeback validation require authenticated user verification through Apple's secure transaction backend."
            elif reason == "high_customer_frustration_or_legal_escalation":
                policy_risk = "Brand Reputation & Legal Risk: Customer exhibits severe agitation or legal escalation. High-touch human specialist intervention is mandated to de-escalate."
            elif reason == "order_logistics_or_warranty_system_lookup":
                policy_risk = "Logistics System Access: Shipping and repair tracking requires direct queries against internal Apple Store order management databases."
            else:
                policy_risk = "Model Uncertainty Risk: Ambiguous user query. Conservatively escalating to prevent customer misinformation."
        else:
            policy_risk = "Low Risk: Issue is non-destructive and fully self-serviceable through official Apple diagnostic steps without human rep overhead."

        # 5. Action Plan
        action_plan = []
        if intent == "HARDWARE_PHYSICAL_DAMAGE":
            action_plan.append("Step 1 (Immediate Safety): Power down device; do NOT plug into charger if moisture is present.")
            action_plan.append("Step 2 (Service Booking): Guide customer to schedule Genius Bar appointment at support.apple.com/repair.")
            action_plan.append("Step 3 (Diagnostics): Certified technician will perform physical seal integrity and component test.")
        elif intent == "ACCOUNT_SECURITY_ICLOUD":
            action_plan.append("Step 1 (Credential Shield): Instruct customer never to disclose passwords/codes in chat or DM.")
            action_plan.append("Step 2 (Self-Recovery): Direct customer to initiate secure recovery at iforgot.apple.com.")
            action_plan.append("Step 3 (Device Audit): Advise reviewing trusted devices under appleid.apple.com.")
        elif intent == "BILLING_SUBSCRIPTION_REFUND":
            action_plan.append("Step 1 (Invoice Audit): Guide customer to reportaproblem.apple.com to inspect itemized receipts.")
            action_plan.append("Step 2 (Refund Filing): Submit automated claim under 'Accidental purchase' or 'Minor purchase'.")
            action_plan.append("Step 3 (Prevention): Enable Screen Time purchasing restrictions in iOS Settings.")
        elif intent == "DEVICE_SETUP_COMPATIBILITY":
            action_plan.append("Step 1 (Prerequisites): Verify Bluetooth and Wi-Fi are active on both devices.")
            action_plan.append("Step 2 (Execution): Follow on-screen guided workflow (e.g. Move to iOS / Apple Watch app).")
            action_plan.append("Step 3 (Verification): Confirm data sync across iCloud and device storage.")
        else: # SOFTWARE_OS_GLITCH
            action_plan.append("Step 1 (Isolation): Check iOS build version under Settings > General > About.")
            action_plan.append("Step 2 (Non-Destructive Fix): Perform forced hardware button restart to flush temporary system cache.")
            action_plan.append("Step 3 (Optimization): Verify storage space and monitor background app usage in Settings > Battery.")

        # 5. Customer Frustration & Urgency Analysis
        frustration = 18
        if any(w in text_lower for w in ["worst", "unacceptable", "scam", "fraud", "thieves", "useless", "lawsuit", "lawyer", "furious", "horrible"]):
            frustration += 45
        if any(w in text_lower for w in ["immediately", "asap", "emergency", "urgent", "cant even", "can't even", "broken", "shattered", "ruined", "lost"]):
            frustration += 25
        if "!" in customer_text:
            frustration += min(customer_text.count("!") * 8, 20)
        # Check for ALL CAPS words
        caps_words = [w for w in customer_text.split() if len(w) >= 4 and w.isupper()]
        if caps_words:
            frustration += 15
        if severity in ["CRITICAL_SAFETY", "HIGH_SECURITY", "HIGH_FINANCIAL"]:
            frustration += 15

        frustration_score = max(10, min(frustration, 98))

        if frustration_score >= 80 or severity == "CRITICAL_SAFETY":
            urgency_level = "CRITICAL"
            sentiment_label = "Highly Agitated / Severe Risk"
        elif frustration_score >= 60 or severity in ["HIGH_SECURITY", "HIGH_FINANCIAL"]:
            urgency_level = "HIGH"
            sentiment_label = "Frustrated & Upset"
        elif frustration_score >= 35:
            urgency_level = "MEDIUM"
            sentiment_label = "Concerned / Inquiring"
        else:
            urgency_level = "LOW"
            sentiment_label = "Calm & Positive"

        # Symptom summary
        symptom_summary = f"Customer reports: {', '.join(signals)} with {severity.replace('_', ' ').lower()} urgency (Frustration: {frustration_score}%)."

        return DiagnosticBreakdown(
            symptom_summary=symptom_summary,
            severity_level=severity,
            detected_signals=signals,
            intent_boundary_rationale=boundary_rationale,
            policy_risk_assessment=policy_risk,
            recommended_action_plan=action_plan,
            frustration_score=frustration_score,
            urgency_level=urgency_level,
            sentiment_label=sentiment_label
        )

    def process_message(
        self,
        customer_text: str,
        context: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AgentOutput:
        """
        Process incoming customer support query through the full agent pipeline with multi-turn memory.
        """
        start_time = time.perf_counter()

        logger.info(f"\n{'='*75}\n[SupportAgent Request] Incoming Query: \"{customer_text}\"\n{'='*75}")

        # Multi-turn context synthesis
        history_context = ""
        if history and len(history) > 1:
            prev_user_msgs = [m["content"] for m in history[:-1] if m.get("role") in ["user", "customer"]]
            if prev_user_msgs:
                history_context = " ".join(prev_user_msgs)
            logger.info(f"[SupportAgent Context Memory] Conversation Turns: {len(history)} | Prior Context: \"{history_context}\"")
        else:
            logger.info(f"[SupportAgent Context Memory] Single-turn query (no prior history)")

        effective_context = f"{context or ''} {history_context}".strip()
        classification_query = f"{customer_text} {history_context}".strip() if history_context else customer_text

        # 1. Intent Classification (with conversational memory grounding)
        clf_result = self.intent_classifier.classify(classification_query)
        predicted_intent = clf_result["predicted_intent"]
        intent_conf = clf_result["confidence"]
        logger.info(f"[SupportAgent Intent] Classified Intent: {predicted_intent} (Confidence: {intent_conf*100:.1f}%)")

        # 2. Escalation & Policy Evaluation
        esc_result: EscalationResult = self.escalation_engine.evaluate(
            customer_text=customer_text,
            predicted_intent=predicted_intent,
            intent_confidence=intent_conf,
            context=effective_context
        )
        logger.info(f"[SupportAgent Escalation] Policy Decision: {esc_result.decision} | Rule: {esc_result.rule_name} | Reason: {esc_result.reason or 'None'}")

        # 3. Knowledge Retrieval (RAG)
        retrieval_query = f"{customer_text} {history_context[:80]}" if history_context else customer_text
        retrieved_docs = self.retriever.retrieve(retrieval_query, top_k=2)
        logger.info(f"[SupportAgent RAG Retrieval] Found {len(retrieved_docs)} Grounding Articles:")
        for idx, doc in enumerate(retrieved_docs, 1):
            logger.info(f"  --> [Article {idx}] Title: \"{doc.get('title', 'N/A')}\" | URL: {doc.get('url', 'N/A')}")
            logger.info(f"      Snippet: \"{doc.get('content', '')[:140]}...\"")

        # 4. Grounded Reply Generation with Multi-Turn Memory
        reply_result = self.reply_generator.generate_reply(
            customer_text=customer_text,
            intent=predicted_intent,
            escalation_decision=esc_result.decision,
            escalation_reason=esc_result.reason,
            retrieved_docs=retrieved_docs,
            context=effective_context,
            history=history
        )

        # 5. Deep Multi-Dimensional Diagnostic Breakdown
        diag = self._generate_deep_diagnostics(
            customer_text=f"{customer_text} {history_context}" if history_context else customer_text,
            intent=predicted_intent,
            intent_conf=intent_conf,
            decision=esc_result.decision,
            reason=esc_result.reason
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.success(f"[SupportAgent Final Output] Latency: {latency_ms:.1f}ms | Source: {reply_result['grounding_source']}\n[Agent Reply]: \"{reply_result['reply_text']}\"\n{'='*75}\n")

        return AgentOutput(
            customer_query=customer_text,
            predicted_intent=predicted_intent,
            intent_confidence=intent_conf,
            decision=esc_result.decision,
            escalation_reason=esc_result.reason,
            escalation_rule_triggered=esc_result.rule_name,
            decision_explanation=diag.policy_risk_assessment,
            diagnostic=diag,
            draft_reply=reply_result["reply_text"],
            grounding_citations=reply_result["citations"],
            grounding_source=reply_result["grounding_source"],
            latency_ms=latency_ms,
            retrieved_knowledge_chunks=retrieved_docs
        )
