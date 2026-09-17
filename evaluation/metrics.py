"""
Automated Quantitative Metrics for Intent Classification and Escalation Decision.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from agent.taxonomy import ALL_INTENTS

def compute_intent_metrics(
    gold_intents: List[str],
    pred_intents: List[str]
) -> Dict[str, Any]:
    """
    Compute Accuracy, Precision, Recall, Macro-F1, Weighted-F1,
    and per-class breakdown for intent classification.
    """
    acc = accuracy_score(gold_intents, pred_intents)
    
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        gold_intents, pred_intents, average="macro", zero_division=0
    )
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(
        gold_intents, pred_intents, average="weighted", zero_division=0
    )

    # Per-class metrics
    prec_per_class, rec_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
        gold_intents, pred_intents, labels=ALL_INTENTS, zero_division=0
    )

    per_class_metrics = {}
    for idx, intent in enumerate(ALL_INTENTS):
        per_class_metrics[intent] = {
            "precision": round(float(prec_per_class[idx]), 4),
            "recall": round(float(rec_per_class[idx]), 4),
            "f1_score": round(float(f1_per_class[idx]), 4),
            "support": int(support_per_class[idx])
        }

    # Confusion matrix
    cm = confusion_matrix(gold_intents, pred_intents, labels=ALL_INTENTS)

    return {
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(prec_macro), 4),
        "macro_recall": round(float(rec_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_f1": round(float(f1_weighted), 4),
        "per_class": per_class_metrics,
        "confusion_matrix": cm.tolist()
    }

def compute_escalation_metrics(
    gold_decisions: List[str],
    pred_decisions: List[str],
    gold_reasons: List[Any],
    pred_reasons: List[Any]
) -> Dict[str, Any]:
    """
    Compute Escalation Accuracy, Precision, Recall, F1,
    False Auto-Handle Rate (dangerous safety failure),
    False Escalation Rate (efficiency loss),
    and Reason Alignment Rate.
    """
    total = len(gold_decisions)
    if total == 0:
        return {}

    # Binary mapping: ESCALATE_TO_HUMAN = 1, AUTO_HANDLE = 0
    y_true = [1 if d == "ESCALATE_TO_HUMAN" else 0 for d in gold_decisions]
    y_pred = [1 if d == "ESCALATE_TO_HUMAN" else 0 for d in pred_decisions]

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)

    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Critical Safety Metric: False Auto-Handle Rate (Under-escalation)
    # Proportion of cases requiring escalation that were mistakenly auto-handled
    false_auto_handle_rate = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    # Efficiency Metric: False Escalation Rate (Over-escalation)
    # Proportion of self-serviceable queries unnecessarily escalated
    false_escalation_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # Reason Alignment: For True Positives, did predicted reason match gold reason?
    reason_matches = 0
    for yt, yp, gr, pr in zip(y_true, y_pred, gold_reasons, pred_reasons):
        if yt == 1 and yp == 1:
            if gr and pr and (gr.lower() in pr.lower() or pr.lower() in gr.lower() or "general" in str(pr).lower()):
                reason_matches += 1
                
    reason_accuracy = (reason_matches / tp) if tp > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_auto_handle_rate": round(false_auto_handle_rate, 4),
        "false_escalation_rate": round(false_escalation_rate, 4),
        "reason_alignment_accuracy": round(reason_accuracy, 4),
        "confusion_breakdown": {
            "true_positives_escalated": tp,
            "false_positives_over_escalated": fp,
            "false_negatives_missed_escalation": fn,
            "true_negatives_auto_handled": tn
        }
    }
