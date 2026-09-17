# Apple Support AI Agent — Production Evaluation & System Benchmark

> **Hiver SDE Intern — Take-Home Assignment Submission**  
> An autonomous AI customer support system for `@AppleSupport` that classifies intents, synthesizes RAG-grounded replies, makes auditable human-escalation decisions, and proves its reliability through rigorous automated and human-aligned evaluations.

📹 **Demo Video**: [Watch System Walkthrough & Dashboard Demo on Google Drive](https://drive.google.com/file/d/1N7Id2arxlGQ9bYcB1jtEM1Y6jmtr_Owl/view?usp=sharing)

---

## ⚡️ 15-Minute Reproduction Quickstart

You can reproduce all headline metrics, run the evaluation harness, and test the agent locally in **under 2 minutes** without requiring paid external API credentials!

### 1. Setup Environment
```bash
# Clone the repo and navigate to directory
cd hiver

# Install dependencies (Python 3.9+)
pip install -r requirements.txt
```

### 2. Reproduce Headline Benchmark Results (< 30 seconds)
```bash
python reproduce.py
```
This single command executes the full **200-sample Golden Evaluation Set** across **Baseline 1 (Trivial)**, **Baseline 2 (Simple Zero-Shot)**, and the **Proposed Agent**, and runs the **50-sample Human-Judge Alignment validation study**.

### 3. Launch Interactive Web Dashboard
```bash
python reproduce.py --serve
# Open http://127.0.0.1:8000 in your browser!
```

### 4. Run Automated Test Suite
```bash
python -m pytest tests/
```

---

## 📊 Headline Benchmark Results ($N = 200$ Golden Set)

| System | Intent Accuracy (%) | Intent Macro-F1 (%) | Escalation Accuracy (%) | Escalation F1 (%) | False Auto-Handle Rate (%) ⚠️ | Judge Quality (1-5) | Judge Pass Rate (%) | Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline 1 (Trivial Heuristic)** | 29.5% | 31.2% | 63.5% | 69.7% | 23.64% | 2.55 | 0.5% | 0.00 ms |
| **Baseline 2 (Simple Zero-Shot)** | 44.5% | 41.9% | 44.5% | 42.5% | 62.73% | 3.13 | 0.0% | 0.38 ms |
| **Proposed Agent (RAG + Guardrails)** ✨ | **78.5%** | **75.1%** | **84.0%** | **87.3%** | **0.00%** | **3.96** | **83.0%** | **1.40 ms** |

> ⚠️ **Key Safety Finding**: The Proposed Agent achieved a **0.00% False Auto-Handle Rate** (zero missed hardware, security, or financial escalations), whereas Baseline 2 dangerously missed **62.73%** of real customer escalations.

---

## 🔬 Evidence: Proving the LLM Judge is Trustworthy

To validate our automated reply evaluator, we conducted a paired **Human vs. LLM-as-Judge Alignment Study** ($N = 50$ stratified samples across good, mediocre, flawed, and unsafe replies):

- **Quadratic Weighted Cohen's Kappa ($\kappa$)**: **0.7390** (Substantial Inter-Annotator Agreement)
- **Binary Pass/Fail Kappa**: **0.8718** (Near-Perfect Safety Agreement)
- **Pearson Correlation ($r$)**: **0.9406** ($p < 0.0001$)
- **Spearman Rank Correlation ($\rho$)**: **0.9288**
- **Mean Absolute Error (MAE)**: **0.426 points** / 5.0
- **Binary Decision Match**: **94.0%** (47 / 50 exact agreement)

---

## 🏗 System Architecture

```
                                  [ Customer Tweet ]
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │ Intent Classifier (TF-IDF │
                            │  + Semantic Prototypes)   │
                            └─────────────┬─────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
       ┌────────────────────────┐                  ┌────────────────────────┐
       │ Hybrid RAG Retriever   │                  │ Multi-Tier Escalation  │
       │ (4.2k Twitter Threads  │                  │ Engine (Safety, PII,   │
       │  + Official Apple KB)  │                  │  Financial, Frustration│
       └────────────┬───────────┘                  └────────────┬───────────┘
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          ▼
                            ┌───────────────────────────┐
                            │ Grounded Reply Generator  │
                            │ (Apple Brand Voice + URLs)│
                            └─────────────┬─────────────┘
                                          │
                                          ▼
                    [ Structured Output: Intent + Decision +
                       Escalation Reason + Reply + Citations ]
```

---

## 📁 Repository Structure

```
hiver/
├── README.md                      # Quickstart reproduction, architecture & results
├── REPORT.md                      # Full 6-page comprehensive technical report
├── reproduce.py                   # Master reproduction CLI & web launcher
├── requirements.txt               # Dependencies
├── data/
│   ├── golden_eval_set.json       # 200 hand-curated & stratified golden test cases
│   ├── golden_eval_set.csv        # CSV version of golden evaluation set
│   ├── golden_sampling_methodology.md # Stratification and annotation documentation
│   ├── benchmark_summary.csv      # Headline benchmark comparative table
│   ├── benchmark_results.json     # Detailed per-item outputs for all 3 systems
│   ├── human_annotations_50.json  # 50 paired human vs judge ratings
│   ├── knowledge_base/            # 4,282 historical Twitter resolutions + Apple KB
│   └── processed/                 # 5,272 cleaned Twitter conversation pairs
├── agent/
│   ├── taxonomy.py                # 7 domain intent definitions & decision boundaries
│   ├── config.py                  # Escalation policies, brand guidelines, URLs
│   ├── intent_classifier.py       # Calibrated few-shot semantic intent classifier
│   ├── retriever.py               # Hybrid RAG retriever over resolutions
│   ├── escalation_engine.py       # Rule-based & cognitive safety escalation engine
│   ├── reply_generator.py         # Grounded brand-voice reply synthesizer
│   └── agent.py                   # Unified SupportAgent pipeline orchestrator
├── baselines/
│   ├── trivial_baseline.py        # Baseline 1: Keyword lookup + canned replies
│   └── simple_baseline.py         # Baseline 2: Generic zero-shot classifier
├── evaluation/
│   ├── metrics.py                 # Classification & Escalation metric functions
│   ├── judge.py                   # Multi-dimensional LLM-as-Judge rubric
│   ├── human_agreement.py         # Cohen's Kappa & correlation alignment runner
│   └── benchmark.py               # Automated benchmark harness comparing 3 systems
├── web_app/
│   ├── app.py                     # FastAPI backend
│   └── static/index.html          # Interactive live dashboard & baseline comparator
└── tests/
    ├── test_agent.py              # End-to-end agent pipeline tests
    ├── test_escalation.py         # Safety trigger & escalation rule tests
    └── test_metrics.py            # Automated metrics & judge unit tests
```

---

## 🎯 Domain Intent Taxonomy

1. `SOFTWARE_OS_GLITCH`: Bugs, crashes, freezes, battery drain after update, Bluetooth drops. *(Auto-Handle)*
2. `HARDWARE_PHYSICAL_DAMAGE`: Cracked screens, water damage, swollen batteries, broken buttons. *(Escalate to Genius Bar)*
3. `ACCOUNT_SECURITY_ICLOUD`: Locked Apple ID, 2FA issues, hacked account alerts. *(Escalate / Secure Portal)*
4. `BILLING_SUBSCRIPTION_REFUND`: Accidental in-app purchases, unrecognized charges, refunds. *(Escalate / Report a Problem)*
5. `DEVICE_SETUP_COMPATIBILITY`: Android migration (Move to iOS), Apple Watch pairing, AirDrop. *(Auto-Handle)*
6. `WARRANTY_ORDER_SHIPPING`: Order tracking, delayed shipments, trade-in kit delivery. *(Escalate to Logistics)*
7. `GENERAL_INQUIRY_FEEDBACK`: Retail store hours, Today at Apple workshops, feature feedback. *(Auto-Handle)*

---


