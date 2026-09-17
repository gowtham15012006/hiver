"""
FastAPI Backend Application for AI Customer Support Agent Web Interface.
Provides endpoints for message processing, side-by-side baseline comparison,
benchmark dataset exploration, and human-judge alignment metrics.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure root workspace in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger

# Configure Loguru to write directly and synchronously to sys.stdout
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    enqueue=False
)

from agent import SupportAgent
from baselines import TrivialBaseline, SimpleZeroShotBaseline
from evaluation.judge import SupportQualityJudge

app = FastAPI(title="Apple Support AI Agent Dashboard", version="1.0.0")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize models
agent = SupportAgent(use_llm=True)
trivial = TrivialBaseline()
simple = SimpleZeroShotBaseline()
judge = SupportQualityJudge()

# Load benchmark cache
GOLDEN_SET_PATH = "data/golden_eval_set.json"
BENCHMARK_RESULTS_PATH = "data/benchmark_results.json"
HUMAN_ANNOTATIONS_PATH = "data/human_annotations_50.json"

class MessageRequest(BaseModel):
    customer_query: str
    context: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Dashboard Loading...</h2>")

@app.post("/api/process")
async def process_single_message(req: MessageRequest):
    """Process message through proposed AI Support Agent with multi-turn memory."""
    logger.info(f"[HTTP POST /api/process] Incoming query: \"{req.customer_query}\" | History turns: {len(req.history) if req.history else 0}")
    out = agent.process_message(req.customer_query, context=req.context, history=req.history)
    logger.success(f"[HTTP 200 /api/process] Intent: {out.predicted_intent} | Decision: {out.decision} | Latency: {out.latency_ms:.1f}ms")
    return JSONResponse(content=out.to_dict())

@app.post("/api/compare")
async def compare_baselines(req: MessageRequest):
    """Run all 3 systems on the same customer query for side-by-side comparison."""
    q = req.customer_query
    ctx = req.context

    # 1. Proposed Agent
    res_agent = agent.process_message(q, context=ctx).to_dict()
    
    # 2. Baseline 1 (Trivial)
    res_trivial = trivial.process_message(q, context=ctx)
    
    # 3. Baseline 2 (Simple Zero-Shot)
    res_simple = simple.process_message(q, context=ctx)

    # Evaluate all 3 with Judge
    j_agent = judge.evaluate_reply(q, res_agent["draft_reply"], res_agent["draft_reply"], res_agent["predicted_intent"], res_agent["decision"]).to_dict()
    j_trivial = judge.evaluate_reply(q, res_trivial["draft_reply"], res_agent["draft_reply"], res_trivial["predicted_intent"], res_trivial["decision"]).to_dict()
    j_simple = judge.evaluate_reply(q, res_simple["draft_reply"], res_agent["draft_reply"], res_simple["predicted_intent"], res_simple["decision"]).to_dict()

    return JSONResponse(content={
        "query": q,
        "proposed_agent": {**res_agent, "judge_evaluation": j_agent},
        "baseline_1_trivial": {**res_trivial, "judge_evaluation": j_trivial},
        "baseline_2_simple": {**res_simple, "judge_evaluation": j_simple}
    })

@app.get("/api/benchmark-summary")
async def get_benchmark_summary():
    """Return cached benchmark results and golden dataset statistics."""
    if os.path.exists(BENCHMARK_RESULTS_PATH):
        with open(BENCHMARK_RESULTS_PATH, "r", encoding="utf-8") as f:
            bench_data = json.load(f)
    else:
        bench_data = {}

    if os.path.exists(GOLDEN_SET_PATH):
        with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
            golden_data = json.load(f)
    else:
        golden_data = []

    return JSONResponse(content={
        "benchmark_results": bench_data,
        "golden_dataset_count": len(golden_data),
        "golden_samples": golden_data[:50]
    })

@app.get("/api/human-agreement")
async def get_human_agreement():
    """Return human-judge alignment data."""
    if os.path.exists(HUMAN_ANNOTATIONS_PATH):
        with open(HUMAN_ANNOTATIONS_PATH, "r", encoding="utf-8") as f:
            annotations = json.load(f)
    else:
        annotations = []
    return JSONResponse(content={"annotations": annotations})
