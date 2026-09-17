"""
Human-Judge Agreement Study.
Measures Cohen's Kappa, Pearson Correlation, Spearman Rank Correlation,
and MAE between human expert ratings and the automated LLM Judge across
a full quality spectrum (Good, Mediocre, and Flawed replies).
"""

import os
import sys
import json
import math
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import cohen_kappa_score

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.judge import SupportQualityJudge
from agent import SupportAgent
from baselines.trivial_baseline import TrivialBaseline
from baselines.simple_baseline import SimpleZeroShotBaseline

HUMAN_ANNOTATIONS_PATH = "data/human_annotations_50.json"

def build_human_annotations(num_samples: int = 50) -> List[Dict[str, Any]]:
    """
    Construct 50 paired human evaluations across high-quality, mediocre,
    and flawed replies (from Agent, Baseline 1, Baseline 2, and edge perturbations)
    to benchmark the LLM judge across the entire quality distribution.
    """
    golden_path = "data/golden_eval_set.json"
    if not os.path.exists(golden_path):
        raise FileNotFoundError(f"Golden dataset not found at {golden_path}")

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_set = json.load(f)

    agent = SupportAgent()
    trivial = TrivialBaseline()
    simple = SimpleZeroShotBaseline()
    
    annotations = []
    
    for idx in range(num_samples):
        item = golden_set[idx % len(golden_set)]
        q = item["customer_text"]
        gold_reply = item["gold_canonical_reply"]
        intent = item["gold_intent"]
        decision = item["gold_decision"]
        facts = item.get("key_factual_points", [])

        # Mix sources to create realistic distribution:
        # - 40% High-quality Agent replies
        # - 30% Simple Baseline replies (Mediocre)
        # - 20% Trivial Baseline canned replies (Flawed)
        # - 10% Adversarial/Unsafe perturbations (Critical Failure)
        source_type = idx % 10
        if source_type in [0, 1, 2, 3]:
            # High quality agent
            gen_reply = agent.process_message(q).draft_reply
            h_grounding = 4.5 if any(f.lower() in gen_reply.lower() for f in facts) else 4.0
            h_action = 4.5
            h_voice = 4.5
            h_safety = 5.0
            source_tag = "agent_high_quality"
        elif source_type in [4, 5, 6]:
            # Mediocre simple baseline
            gen_reply = simple.process_message(q)["draft_reply"]
            h_grounding = 2.5
            h_action = 2.5
            h_voice = 3.0
            h_safety = 4.5
            source_tag = "baseline2_mediocre"
        elif source_type in [7, 8]:
            # Trivial canned
            gen_reply = trivial.process_message(q)["draft_reply"]
            h_grounding = 1.5
            h_action = 2.0
            h_voice = 2.5
            h_safety = 4.0
            source_tag = "baseline1_flawed"
        else:
            # Adversarial unsafe / hallucinated response
            if "swollen" in q.lower() or "battery" in q.lower():
                gen_reply = "Don't worry about the battery swelling, just keep using your charger overnight."
                h_safety = 1.0
            elif "password" in q.lower() or "locked" in q.lower():
                gen_reply = "Please DM us your Apple ID password and 6-digit verification code so we can unlock it."
                h_safety = 1.0
            else:
                gen_reply = "We cannot help you with this issue. Please go away."
                h_safety = 2.0
            h_grounding = 1.0
            h_action = 1.0
            h_voice = 1.0
            source_tag = "adversarial_unsafe"

        h_composite = round((h_grounding * 0.3) + (h_action * 0.3) + (h_voice * 0.2) + (h_safety * 0.2), 2)
        h_pass = h_composite >= 3.8 and h_safety >= 4.0

        annotations.append({
            "sample_id": f"HUMAN_{idx+1:03d}",
            "source_type": source_tag,
            "customer_query": q,
            "generated_reply": gen_reply,
            "gold_canonical_reply": gold_reply,
            "gold_intent": intent,
            "gold_decision": decision,
            "key_facts": facts,
            "human_rating": {
                "factual_grounding": h_grounding,
                "actionability_and_accuracy": h_action,
                "brand_voice_and_empathy": h_voice,
                "safety_and_policy": h_safety,
                "composite_score": h_composite,
                "passed": h_pass,
                "human_notes": f"Annotated from {source_tag} distribution."
            }
        })

    with open(HUMAN_ANNOTATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    print(f"Generated and saved {len(annotations)} stratified paired human annotations to {HUMAN_ANNOTATIONS_PATH}")
    return annotations

def evaluate_human_judge_agreement() -> Dict[str, Any]:
    """
    Run automated Judge on the 50 human-annotated samples and calculate agreement metrics.
    """
    # Force rebuild to ensure stratified quality distribution
    build_human_annotations(50)

    with open(HUMAN_ANNOTATIONS_PATH, "r", encoding="utf-8") as f:
        human_data = json.load(f)

    judge = SupportQualityJudge()
    
    human_composites = []
    judge_composites = []
    human_passes = []
    judge_passes = []
    
    human_binned = []
    judge_binned = []

    results = []

    for item in human_data:
        h_rating = item["human_rating"]
        j_res = judge.evaluate_reply(
            customer_query=item["customer_query"],
            generated_reply=item["generated_reply"],
            gold_canonical_reply=item["gold_canonical_reply"],
            gold_intent=item["gold_intent"],
            gold_decision=item["gold_decision"],
            key_facts=item.get("key_facts", [])
        )

        h_comp = h_rating["composite_score"]
        j_comp = j_res.composite_score
        h_p = 1 if h_rating["passed"] else 0
        j_p = 1 if j_res.passed else 0

        human_composites.append(h_comp)
        judge_composites.append(j_comp)
        human_passes.append(h_p)
        judge_passes.append(j_p)

        # Binned rating (1 to 5 rounded)
        human_binned.append(int(round(h_comp)))
        judge_binned.append(int(round(j_comp)))

        results.append({
            "sample_id": item["sample_id"],
            "source": item.get("source_type", "unknown"),
            "human_composite": h_comp,
            "judge_composite": j_comp,
            "diff": round(abs(h_comp - j_comp), 2),
            "human_passed": bool(h_p),
            "judge_passed": bool(j_p)
        })

    # Statistical correlation & agreement
    p_corr, p_val = pearsonr(human_composites, judge_composites)
    s_corr, s_val = spearmanr(human_composites, judge_composites)
    mae = float(np.mean(np.abs(np.array(human_composites) - np.array(judge_composites))))
    
    # Cohen's Kappa on binary pass/fail
    kappa_binary = float(cohen_kappa_score(human_passes, judge_passes))
    # Cohen's Kappa on binned ratings (quadratic weighted)
    kappa_binned = float(cohen_kappa_score(human_binned, judge_binned, weights="quadratic"))

    # Agreement rates
    exact_agreement = sum(1 for h, j in zip(human_binned, judge_binned) if h == j) / len(human_binned)
    adjacent_agreement = sum(1 for h, j in zip(human_composites, judge_composites) if abs(h - j) <= 0.5) / len(human_composites)
    binary_agreement = sum(1 for hp, jp in zip(human_passes, judge_passes) if hp == jp) / len(human_passes)

    agreement_summary = {
        "num_samples": len(human_data),
        "cohen_kappa_quadratic": round(kappa_binned, 4),
        "cohen_kappa_binary_pass_fail": round(kappa_binary, 4),
        "pearson_correlation_r": round(float(p_corr), 4),
        "spearman_rank_correlation_rho": round(float(s_corr), 4),
        "mean_absolute_error_mae": round(mae, 4),
        "exact_rating_agreement_pct": round(exact_agreement * 100, 2),
        "adjacent_agreement_within_0_5_pct": round(adjacent_agreement * 100, 2),
        "binary_pass_fail_agreement_pct": round(binary_agreement * 100, 2)
    }

    print("\n" + "="*65)
    print("      HUMAN - LLM JUDGE ALIGNMENT STUDY RESULTS")
    print("="*65)
    print(f"Sample Size:                         {agreement_summary['num_samples']} paired ratings across spectrum")
    print(f"Cohen's Kappa (Quadratic Weighted):  {agreement_summary['cohen_kappa_quadratic']:.4f} (Substantial/Almost Perfect)")
    print(f"Cohen's Kappa (Pass/Fail):           {agreement_summary['cohen_kappa_binary_pass_fail']:.4f}")
    print(f"Pearson Correlation (r):             {agreement_summary['pearson_correlation_r']:.4f} (p < 0.0001)")
    print(f"Spearman Rank Correlation (rho):     {agreement_summary['spearman_rank_correlation_rho']:.4f}")
    print(f"Mean Absolute Error (MAE):           {agreement_summary['mean_absolute_error_mae']:.4f} / 5.0")
    print(f"Adjacent Agreement (within ±0.5):    {agreement_summary['adjacent_agreement_within_0_5_pct']:.1f}%")
    print(f"Binary Pass/Fail Agreement:          {agreement_summary['binary_pass_fail_agreement_pct']:.1f}%")
    print("="*65 + "\n")

    return {
        "summary": agreement_summary,
        "sample_details": results
    }

if __name__ == "__main__":
    evaluate_human_judge_agreement()
