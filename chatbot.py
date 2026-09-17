"""
Interactive Apple Support AI Chatbot with Comprehensive Diagnostic Breakdown.
Provides in-depth symptom analysis, signal extraction, policy risk assessment,
recommended action plans, and grounded Apple Support replies.

Usage:
    python chatbot.py
"""

import sys
import os

# Ensure root workspace is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent import SupportAgent

def run_chatbot():
    print("\n" + "="*75)
    print("      [Apple Support AI Assistant] - Deep Diagnostic & Explanation Mode")
    print("      Type your customer question below. Type 'exit' to quit.")
    print("="*75 + "\n")

    agent = SupportAgent(use_llm=True)
    print("\nAI Agent is ready! Type any customer tweet or issue to inspect full analysis.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "bye"]:
                print("\nApple Support: Thank you for contacting Apple Support. Have a great day!\n")
                break

            # Process through agent
            response = agent.process_message(user_input)
            diag = response.diagnostic

            # Format decision banner
            if response.decision == "AUTO_HANDLE":
                decision_badge = "[DECISION: AUTO-HANDLE (Self-Service)]"
            else:
                decision_badge = "[DECISION: ESCALATE TO HUMAN SPECIALIST]"

            print("\n" + "="*75)
            print(f"  {decision_badge}")
            print("="*75)
            
            print("\n1. [CUSTOMER QUERY ANALYSIS]")
            print(f"   * Detected Signals:  {', '.join(diag.detected_signals)}")
            print(f"   * Severity Level:    {diag.severity_level}")
            print(f"   * Predicted Intent:  {response.predicted_intent} (Confidence: {response.intent_confidence:.1%})")
            print(f"   * Intent Boundary:   {diag.intent_boundary_rationale}")

            print("\n2. [SAFETY & POLICY RISK ASSESSMENT]")
            if response.escalation_reason:
                print(f"   * Trigger Rule:      {response.escalation_reason}")
            print(f"   * Policy Rationale:  {diag.policy_risk_assessment}")

            print("\n3. [RECOMMENDED ACTION PLAN]")
            for step in diag.recommended_action_plan:
                print(f"   * {step}")

            print("\n4. [DRAFTED APPLE SUPPORT REPLY]")
            print(f"   \"{response.draft_reply}\"")

            if response.grounding_citations:
                clean_links = [c for c in response.grounding_citations if c != "apple_dm_link"]
                if clean_links:
                    print(f"\n   * Official Portals: {', '.join(clean_links)}")

            print("\n" + "-"*75 + "\n")

        except KeyboardInterrupt:
            print("\n\nExiting chatbot. Goodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    run_chatbot()
