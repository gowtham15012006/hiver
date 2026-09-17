"""
Unit tests for SupportAgent orchestrator.
"""

import pytest
from agent import SupportAgent, AgentOutput
from agent.taxonomy import ALL_INTENTS

@pytest.fixture(scope="module")
def agent():
    return SupportAgent(use_llm=False)

def test_agent_software_glitch_autohandle(agent):
    query = "@AppleSupport Battery health dropped 20% in one week and phone is warm after update."
    res = agent.process_message(query)
    assert isinstance(res, AgentOutput)
    assert res.predicted_intent == "SOFTWARE_OS_GLITCH"
    assert res.decision == "AUTO_HANDLE"
    assert "Settings > Battery" in res.draft_reply or "indexing" in res.draft_reply or "restart" in res.draft_reply
    assert len(res.grounding_citations) > 0

def test_agent_hardware_damage_escalate(agent):
    query = "@AppleSupport Dropped my iPhone in the swimming pool, speaker crackles and screen has green lines."
    res = agent.process_message(query)
    assert res.predicted_intent == "HARDWARE_PHYSICAL_DAMAGE"
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.escalation_reason == "requires_hardware_inspection_or_genius_bar"
    assert "repair" in res.draft_reply.lower()

def test_agent_account_security_escalate(agent):
    query = "@AppleSupport My Apple ID is locked and I cannot receive 2FA verification codes."
    res = agent.process_message(query)
    assert res.predicted_intent == "ACCOUNT_SECURITY_ICLOUD"
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.escalation_reason == "security_sensitive_credentials_or_account_lockout"
    assert "iforgot.apple.com" in res.draft_reply or "appleid.apple.com" in res.draft_reply

def test_agent_billing_refund_escalate(agent):
    query = "@AppleSupport I was charged $99.99 for an in-app subscription my child bought by accident."
    res = agent.process_message(query)
    assert res.predicted_intent == "BILLING_SUBSCRIPTION_REFUND"
    assert res.decision == "ESCALATE_TO_HUMAN"
    assert res.escalation_reason == "financial_transaction_and_refund_authorization"
    assert "reportaproblem.apple.com" in res.draft_reply

def test_agent_setup_compatibility_autohandle(agent):
    query = "@AppleSupport How do I transfer my data from Android to my new iPhone 13?"
    res = agent.process_message(query)
    assert res.predicted_intent == "DEVICE_SETUP_COMPATIBILITY"
    assert res.decision == "AUTO_HANDLE"
    assert "Move to iOS" in res.draft_reply or "setup" in res.draft_reply.lower()

def test_agent_latency(agent):
    res = agent.process_message("@AppleSupport Test message")
    assert res.latency_ms < 50.0  # Under 50ms requirement
