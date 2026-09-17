"""
Rule-based & Cognitive Escalation Engine for Customer Support.
Evaluates explicit safety triggers, customer sentiment, multi-turn history, and intent policies.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from agent.config import (
    ESCALATION_RULES,
    ANGER_LEGAL_KEYWORDS,
    REPEATED_FAILURE_KEYWORDS
)
from agent.taxonomy import INTENT_TAXONOMY

@dataclass
class EscalationResult:
    decision: str  # "AUTO_HANDLE" or "ESCALATE_TO_HUMAN"
    reason: Optional[str]
    rule_name: Optional[str]
    confidence: float
    trigger_evidence: Optional[str]

class EscalationEngine:
    """
    Evaluates incoming customer messages to decide between AUTO_HANDLE
    and ESCALATE_TO_HUMAN, providing explicit audit reasons.
    """
    def __init__(self, confidence_threshold: float = 0.25):
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        customer_text: str,
        predicted_intent: str,
        intent_confidence: float,
        context: Optional[str] = None
    ) -> EscalationResult:
        """
        Evaluate customer message and return structured escalation decision.
        """
        text_lower = customer_text.lower()
        combined_text = f"{text_lower} {context.lower() if context else ''}"

        # 1. Check Extreme Frustration / Legal Threats (Highest Priority)
        for kw in ANGER_LEGAL_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="high_customer_frustration_or_legal_escalation",
                    rule_name="HIGH_FRUSTRATION_OR_LEGAL",
                    confidence=0.98,
                    trigger_evidence=f"Matched anger/legal keyword: '{kw}'"
                )

        # 2. Check Repeated Troubleshooting Failure
        for kw in REPEATED_FAILURE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="unresolved_after_standard_troubleshooting",
                    rule_name="REPEATED_FAILURE_AFTER_TROUBLESHOOTING",
                    confidence=0.95,
                    trigger_evidence=f"Customer indicated previous attempts failed: '{kw}'"
                )

        # 3. Check Hardware / Physical / Thermal Safety Triggers
        hardware_triggers = ["cracked", "broken screen", "shattered", "water", "pool", "toilet", "swollen", "smoke", "spark", "submerged", "bent chassis", "snapped pin", "burning"]
        for hw in hardware_triggers:
            if hw in text_lower:
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="requires_hardware_inspection_or_genius_bar",
                    rule_name="HARDWARE_SAFETY_OR_DAMAGE",
                    confidence=0.95,
                    trigger_evidence=f"Detected physical/hardware hazard: '{hw}'"
                )

        # 4. Check Account Security / 2FA / Compromise Triggers
        security_triggers = ["locked apple id", "apple id locked", "iforgot", "2fa", "two-factor", "verification code", "hacked", "stolen iphone", "activation lock", "compromised"]
        for sec in security_triggers:
            if sec in text_lower:
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="security_sensitive_credentials_or_account_lockout",
                    rule_name="ACCOUNT_SECURITY_LOCKOUT",
                    confidence=0.95,
                    trigger_evidence=f"Detected credential/security trigger: '{sec}'"
                )

        # 5. Check Direct Billing Dispute / Refund Requests
        billing_triggers = ["unauthorized charge", "charged twice", "refund", "stole money", "card declined", "dispute charge", "wrong bill", "double charged"]
        for bill in billing_triggers:
            if bill in text_lower:
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="financial_transaction_and_refund_authorization",
                    rule_name="FINANCIAL_OR_BILLING_DISPUTE",
                    confidence=0.95,
                    trigger_evidence=f"Detected financial transaction trigger: '{bill}'"
                )

        # 6. Check Order Logistics / Shipping Status Lookups
        order_triggers = ["order status", "ups", "fedex", "tracking number", "lost package", "trade-in kit", "repair id", "preparing for shipment"]
        for ord_t in order_triggers:
            if ord_t in text_lower:
                return EscalationResult(
                    decision="ESCALATE_TO_HUMAN",
                    reason="order_logistics_or_warranty_system_lookup",
                    rule_name="ORDER_OR_WARRANTY_LOOKUP",
                    confidence=0.92,
                    trigger_evidence=f"Detected order logistics trigger: '{ord_t}'"
                )

        # 7. Check Low Confidence / Ambiguity Fallback
        if intent_confidence < self.confidence_threshold:
            return EscalationResult(
                decision="ESCALATE_TO_HUMAN",
                reason="low_confidence_ambiguous_intent",
                rule_name="LOW_CONFIDENCE_FALLBACK",
                confidence=round(1.0 - intent_confidence, 2),
                trigger_evidence=f"Intent confidence ({intent_confidence:.2f}) below threshold ({self.confidence_threshold:.2f})"
            )

        # 8. Intent Default Policy
        intent_def = INTENT_TAXONOMY.get(predicted_intent)
        if intent_def and intent_def.default_action == "ESCALATE_TO_HUMAN":
            return EscalationResult(
                decision="ESCALATE_TO_HUMAN",
                reason=intent_def.default_escalation_reason or "requires_human_specialist_intervention",
                rule_name=f"INTENT_DEFAULT_{predicted_intent}",
                confidence=0.90,
                trigger_evidence=f"Intent '{predicted_intent}' mandates human escalation by brand policy."
            )

        # 9. Default: Auto-Handle
        return EscalationResult(
            decision="AUTO_HANDLE",
            reason=None,
            rule_name="STANDARD_SELF_SERVICE_POLICY",
            confidence=0.92,
            trigger_evidence="No safety, financial, security, or escalation triggers fired."
        )
