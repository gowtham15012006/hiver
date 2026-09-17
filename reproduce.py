"""
Master Reproduction Script for Hiver SDE Intern AI Customer Support Agent.
Reproduce all headline benchmark numbers, human-judge alignment, and test live queries in < 5 minutes.

Usage:
  python reproduce.py                # Run full benchmark and human-judge alignment
  python reproduce.py --quick        # Quick run on subset of test cases
  python reproduce.py --interactive  # Interactive terminal session
  python reproduce.py --serve        # Launch local Web UI dashboard (FastAPI)
"""

import os
import sys
import argparse
import time
import json
import pandas as pd

from agent import SupportAgent
from evaluation.benchmark import run_benchmark
from evaluation.human_agreement import evaluate_human_judge_agreement

def main():
    parser = argparse.ArgumentParser(description="Hiver AI Support Agent - Master Reproduction Suite")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark on first 50 golden samples")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive CLI tester")
    parser.add_argument("--llm", action="store_true", help="Enable live Gemini LLM generation in interactive mode")
    parser.add_argument("--serve", action="store_true", help="Launch interactive Web Dashboard on http://127.0.0.1:8000")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server (default 8000)")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        from web_app.app import app
        print(f"\n=======================================================")
        print(f"  Launching AI Support Agent Web UI on http://127.0.0.1:{args.port}")
        print(f"=======================================================\n")
        uvicorn.run("web_app.app:app", host="127.0.0.1", port=args.port, reload=True)
        return

    if args.interactive:
        run_interactive_cli(use_llm=args.llm)
        return

    # Default: Run Full Headline Benchmark & Human-Judge Alignment
    print("\n" + "="*80)
    print("      HIVER SDE INTERN TAKE-HOME ASSIGNMENT - EVALUATION BENCHMARK")
    print("="*80)
    print("Reproducing Headline Results across 200 Golden Evaluation Set Examples...\n")

    start_bench = time.perf_counter()
    eval_path = "data/golden_eval_set.json"
    
    # Run Benchmark
    benchmark_res = run_benchmark(eval_path=eval_path)
    
    # Run Human-Judge Alignment
    print("\nRunning Human-Judge Alignment Validation Study (50 Paired Samples)...")
    agreement_res = evaluate_human_judge_agreement()

    total_time = round(time.perf_counter() - start_bench, 2)
    print("\n" + "="*80)
    print(f"   REPRODUCTION COMPLETE IN {total_time} SECONDS (Target: < 15 minutes)")
    print("="*80)
    print(f"Summary Table saved to:   data/benchmark_summary.csv")
    print(f"Detailed Results saved to: data/benchmark_results.json")
    print(f"Human Alignment saved to: data/human_annotations_50.json")
    print("="*80 + "\n")

def run_interactive_cli(use_llm: bool = False):
    print("\n" + "="*60)
    print(f"  Apple Support AI Agent - Interactive Terminal Mode (LLM: {'Gemini Live' if use_llm else 'Grounded Fast Engine'})")
    print("  Type your customer support message or 'exit' to quit.")
    print("="*60 + "\n")

    agent = SupportAgent(use_llm=use_llm)

    while True:
        try:
            query = input("\n[Customer Tweet] > ").strip()
            if not query or query.lower() in ["exit", "quit", "q"]:
                print("Exiting interactive mode.")
                break

            out = agent.process_message(query)
            print("\n" + "-"*50)
            print(f"Predicted Intent:     {out.predicted_intent} (Confidence: {out.intent_confidence:.2f})")
            print(f"Decision:             {out.decision}")
            if out.escalation_reason:
                print(f"Escalation Reason:    {out.escalation_reason}")
                print(f"Trigger Rule:         {out.escalation_rule_triggered}")
            print(f"Latency:              {out.latency_ms:.2f} ms")
            print(f"Grounding Citations:  {', '.join(out.grounding_citations) if out.grounding_citations else 'None'}")
            print("\n[Agent Draft Reply]:")
            print(out.draft_reply)
            print("-"*50)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
