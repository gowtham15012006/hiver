"""
Unit tests for EscalationEngine safety triggers and rules.
"""

import pytest
from agent.escalation_engine import EscalationEngine, EscalationResult

@pytest.fixture
def engine():
    return EscalationEngine()

def test_anger_legal_threat_escalation(engine):
    res = engine.evaluate(
        customer_text="@AppleSupport You guys are scamming me, I am hiring a lawyer and suing you!",
        predicted_intent="BILLING_SUBSCRIPTION_REFUND",
        intent_confidence=0.85
    )
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.reason == "high_customer_frustration_or_legal_escalation"
    assert res.rule_name == "HIGH_FRUSTRATION_OR_LEGAL"

def test_repeated_failure_escalation(engine):
    res = engine.evaluate(
        customer_text="@AppleSupport I already restarted twice and reset network settings, still not working.",
        predicted_intent="SOFTWARE_OS_GLITCH",
        intent_confidence=0.80
    )
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.reason == "unresolved_after_standard_troubleshooting"

def test_swollen_battery_hazard_escalation(engine):
    res = engine.evaluate(
        customer_text="@AppleSupport My MacBook battery is swollen and trackpad popped out.",
        predicted_intent="HARDWARE_PHYSICAL_DAMAGE",
        intent_confidence=0.90
    )
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.reason == "requires_hardware_inspection_or_genius_bar"

def test_standard_setup_autohandle(engine):
    res = engine.evaluate(
        customer_text="@AppleSupport How do I enable Night Shift on my MacBook?",
        predicted_intent="DEVICE_SETUP_COMPATIBILITY",
        intent_confidence=0.85
    )
    assert res.decision == "AUTO_HANDLE"
    assert res.reason is None
