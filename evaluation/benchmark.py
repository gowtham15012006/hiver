"""
Comprehensive Benchmark Runner comparing:
1. Baseline 1 (Trivial Heuristic)
2. Baseline 2 (Simple Zero-Shot)
3. Proposed System (AI Support Agent with RAG & Policy Guardrails)
across the 200 Golden Evaluation Examples.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any
import pandas as pd

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent import SupportAgent
from baselines import TrivialBaseline, SimpleZeroShotBaseline
from evaluation.metrics import compute_intent_metrics, compute_escalation_metrics
from evaluation.judge import SupportQualityJudge

BENCHMARK_RESULTS_JSON = "data/benchmark_results.json"
BENCHMARK_SUMMARY_CSV = "data/benchmark_summary.csv"

def run_benchmark(eval_path: str = "data/golden_eval_set.json") -> Dict[str, Any]:
    """
    Run complete benchmark on the golden evaluation dataset across all 3 systems.
    """
    if not os.path.exists(eval_path):
        raise FileNotFoundError(f"Golden dataset not found at {eval_path}")

    with open(eval_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    print(f"\n========================================================")
    print(f"   STARTING COMPREHENSIVE BENCHMARK ON {len(golden_data)} GOLD EXAMPLES")
    print(f"========================================================\n")

    systems = {
        "Baseline 1 (Trivial)": TrivialBaseline(),
        "Baseline 2 (Simple Zero-Shot)": SimpleZeroShotBaseline(),
        "Proposed Agent (RAG + Guardrails)": SupportAgent(use_llm=False)
    }

    judge = SupportQualityJudge()
    all_system_results = {}

    gold_intents = [item["gold_intent"] for item in golden_data]
    gold_decisions = [item["gold_decision"] for item in golden_data]
    gold_reasons = [item["gold_escalation_reason"] for item in golden_data]

    summary_rows = []

    for sys_name, system in systems.items():
        print(f"--> Evaluating [{sys_name}]...")
        start_t = time.perf_counter()
        
        pred_intents = []
        pred_decisions = []
        pred_reasons = []
        draft_replies = []
        latencies = []
        judge_scores = []
        judge_passes = []

        detailed_outputs = []

        for idx, item in enumerate(golden_data):
            q = item["customer_text"]
            ctx = item.get("context")
            gold_reply = item["gold_canonical_reply"]
            key_facts = item.get("key_factual_points", [])

            # Run system
            if hasattr(system, "process_message"):
                res = system.process_message(q, context=ctx)
                # Res could be AgentOutput dataclass or dict
                if hasattr(res, "to_dict"):
                    res_dict = res.to_dict()
                else:
                    res_dict = res
            else:
                raise ValueError("System missing process_message")

            pred_intent = res_dict["predicted_intent"]
            pred_dec = res_dict["decision"]
            pred_reason = res_dict.get("escalation_reason")
            reply = res_dict["draft_reply"]
            latency = res_dict.get("latency_ms", 0.0)

            pred_intents.append(pred_intent)
            pred_decisions.append(pred_dec)
            pred_reasons.append(pred_reason)
            draft_replies.append(reply)
            latencies.append(latency)

            # Run Judge on generated reply
            j_eval = judge.evaluate_reply(
                customer_query=q,
                generated_reply=reply,
                gold_canonical_reply=gold_reply,
                gold_intent=item["gold_intent"],
                gold_decision=item["gold_decision"],
                key_facts=key_facts
            )
            judge_scores.append(j_eval.composite_score)
            judge_passes.append(1 if j_eval.passed else 0)

            detailed_outputs.append({
                "id": item["id"],
                "query": q,
                "gold_intent": item["gold_intent"],
                "pred_intent": pred_intent,
                "gold_decision": item["gold_decision"],
                "pred_decision": pred_dec,
                "gold_reason": item["gold_escalation_reason"],
                "pred_reason": pred_reason,
                "draft_reply": reply,
                "judge_composite": j_eval.composite_score,
                "judge_passed": j_eval.passed,
                "judge_feedback": j_eval.feedback
            })

        total_sys_time = time.perf_counter() - start_t
        avg_latency = float(pd.Series(latencies).mean()) if latencies else 0.0

        # Compute Intent Classification Metrics
        intent_m = compute_intent_metrics(gold_intents, pred_intents)
        # Compute Escalation Decision Metrics
        escalation_m = compute_escalation_metrics(gold_decisions, pred_decisions, gold_reasons, pred_reasons)
        
        avg_judge_score = float(pd.Series(judge_scores).mean())
        judge_pass_rate = float(pd.Series(judge_passes).mean()) * 100.0

        sys_metrics = {
            "intent_metrics": intent_m,
            "escalation_metrics": escalation_m,
            "judge_metrics": {
                "mean_quality_score": round(avg_judge_score, 2),
                "pass_rate_pct": round(judge_pass_rate, 2)
            },
            "performance": {
                "total_time_sec": round(total_sys_time, 2),
                "avg_latency_ms": round(avg_latency, 2)
            },
            "detailed_outputs": detailed_outputs
        }

        all_system_results[sys_name] = sys_metrics

        summary_rows.append({
            "System": sys_name,
            "Intent Accuracy (%)": round(intent_m["accuracy"] * 100, 2),
            "Intent Macro-F1 (%)": round(intent_m["macro_f1"] * 100, 2),
            "Escalation Accuracy (%)": round(escalation_m["accuracy"] * 100, 2),
            "Escalation F1 (%)": round(escalation_m["f1_score"] * 100, 2),
            "False Auto-Handle Rate (%)": round(escalation_m["false_auto_handle_rate"] * 100, 2),
            "Judge Quality (1-5)": round(avg_judge_score, 2),
            "Judge Pass Rate (%)": round(judge_pass_rate, 2),
            "Avg Latency (ms)": round(avg_latency, 2)
        })

    # Output Summary Table
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(BENCHMARK_SUMMARY_CSV, index=False)

    with open(BENCHMARK_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_system_results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*85)
    print("                      HEADLINE BENCHMARK COMPARISON RESULTS")
    print("="*85)
    print(df_summary.to_string(index=False))
    print("="*85 + "\n")

    return {
        "summary_table": summary_rows,
        "full_results": all_system_results
    }

if __name__ == "__main__":
    run_benchmark()
