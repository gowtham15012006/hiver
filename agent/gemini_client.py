"""
Gemini API Client for Live Dynamic Generation.
Uses Google Gemini REST API with multi-model fallback and loguru diagnostic tracing.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from loguru import logger

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
CANDIDATE_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

class GeminiClient:
    """
    Google Gemini Client for generating dynamic grounded replies with multi-turn memory
    and structured loguru diagnostic tracing.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or DEFAULT_GEMINI_KEY
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        masked_key = self.api_key[:4] + "..." + self.api_key[-4:] if self.api_key and len(self.api_key) > 8 else "***"
        self.masked_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={masked_key}"
        logger.info(f"[LLM Init] Initialized GeminiClient | Model: {self.model} | Endpoint: {self.masked_endpoint}")

    def generate(self, prompt: str, system_instruction: Optional[str] = None, max_tokens: int = 350) -> Optional[str]:
        """
        Generate text completion using Google Gemini API with detailed loguru tracing and multi-model failover.
        """
        if not self.api_key:
            logger.warning("[LLM Request] Missing Gemini API key. Skipping LLM generation.")
            return None

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.2
            }
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        prompt_preview = prompt.replace("\n", " ")[:120] + "..." if len(prompt) > 120 else prompt.replace("\n", " ")
        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]

        for current_model in models_to_try:
            endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={self.api_key}"
            masked_key = self.api_key[:4] + "..." + self.api_key[-4:] if self.api_key and len(self.api_key) > 8 else "***"
            masked_url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={masked_key}"

            logger.info(f"[LLM Processing State] SENDING_REQUEST | Model: {current_model} | Endpoint: {masked_url}")
            logger.info(f"[LLM System Instruction]: \"{system_instruction}\"")
            logger.info(f"[LLM Prompt Payload]:\n\"\"\"\n{prompt}\n\"\"\"")

            start_time = time.perf_counter()
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    endpoint_url,
                    data=data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    result = json.loads(resp.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            reply_text = parts[0]["text"].strip()
                            logger.success(f"[LLM Response State] SUCCESS | Model: {current_model} | Latency: {elapsed_ms:.1f}ms\n[LLM Generated Text]: \"{reply_text}\"")
                            return reply_text
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.warning(f"[LLM Response State] FAILOVER_TRIGGERED | Model: {current_model} | Latency: {elapsed_ms:.1f}ms | Error: {e}")
                continue

        return None

    def generate_chat(self, history: List[Dict[str, str]], system_instruction: Optional[str] = None, max_tokens: int = 350) -> Optional[str]:
        """
        Generate contextual reply using multi-turn conversation memory with loguru tracing.
        """
        if not self.api_key or not history:
            return None

        contents = []
        for msg in history:
            role = "user" if msg.get("role") in ["user", "customer"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.25
            }
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]

        for current_model in models_to_try:
            endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={self.api_key}"
            masked_key = self.api_key[:4] + "..." + self.api_key[-4:] if self.api_key and len(self.api_key) > 8 else "***"
            masked_url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={masked_key}"

            logger.info(f"[LLM Chat Request] SENDING_MULTI_TURN | Model: {current_model} | Turns: {len(history)} | Endpoint: {masked_url}")

            start_time = time.perf_counter()
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    endpoint_url,
                    data=data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    result = json.loads(resp.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            reply_text = parts[0]["text"].strip()
                            logger.success(f"[LLM Chat Response] SUCCESS | Model: {current_model} | Latency: {elapsed_ms:.1f}ms")
                            return reply_text
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.warning(f"[LLM Chat Response] FAILOVER_TRIGGERED | Model: {current_model} | Latency: {elapsed_ms:.1f}ms | Error: {e}")
                continue

        return None
