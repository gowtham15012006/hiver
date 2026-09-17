"""
Unit tests for evaluation metrics and judge.
"""

import pytest
from evaluation.metrics import compute_intent_metrics, compute_escalation_metrics
from evaluation.judge import SupportQualityJudge

def test_intent_metrics():
    gold = ["SOFTWARE_OS_GLITCH", "HARDWARE_PHYSICAL_DAMAGE", "ACCOUNT_SECURITY_ICLOUD"]
    pred = ["SOFTWARE_OS_GLITCH", "HARDWARE_PHYSICAL_DAMAGE", "ACCOUNT_SECURITY_ICLOUD"]
    m = compute_intent_metrics(gold, pred)
    assert m["accuracy"] == 1.0
    assert m["macro_f1"] == 1.0

def test_escalation_metrics_under_escalation():
    # 2 true escalations, 1 missed (false auto-handle)
    gold = ["ESCALATE_TO_HUMAN", "ESCALATE_TO_HUMAN", "AUTO_HANDLE"]
    pred = ["ESCALATE_TO_HUMAN", "AUTO_HANDLE", "AUTO_HANDLE"]
    gold_r = ["reason_a", "reason_b", None]
    pred_r = ["reason_a", None, None]
    m = compute_escalation_metrics(gold, pred, gold_r, pred_r)
    assert m["false_auto_handle_rate"] == 0.5  # 1 out of 2 missed
    assert m["recall"] == 0.5

def test_judge_quality_pass():
    judge = SupportQualityJudge()
    res = judge.evaluate_reply(
        customer_query="@AppleSupport How do I cancel my Apple TV subscription?",
        generated_reply="You can cancel your subscription directly in Settings > [Your Name] > Subscriptions > tap Cancel. Visit https://support.apple.com for more info.",
        gold_canonical_reply="Go to Settings > Name > Subscriptions.",
        gold_intent="BILLING_SUBSCRIPTION_REFUND",
        gold_decision="AUTO_HANDLE",
        key_facts=["Settings > [Your Name] > Subscriptions", "Cancel button"]
    )
    assert res.passed is True
    assert res.composite_score >= 3.8
    assert res.safety_and_policy == 5.0
