"""
Script to stream, extract, clean, and structure AppleSupport conversations from the Customer Support on Twitter dataset.
"""

import os
import io
import re
import csv
import json
import html
import urllib.request
from typing import Dict, List, Any, Optional

TWCS_URL = "https://huggingface.co/datasets/SunidhiSriram/twcs/resolve/main/twcs.csv"
RAW_CACHE_FILE = "data/raw/applesupport_raw_sample.csv"
PROCESSED_FILE = "data/processed/applesupport_dialogues.json"
KB_FILE = "data/knowledge_base/resolutions.json"

def clean_tweet_text(text: str) -> str:
    """Clean tweet text while preserving semantics and intent."""
    if not text:
        return ""
    # Unescape HTML entities
    text = html.unescape(text)
    # Replace anonymized twitter handles like @115854 with @user / @customer
    text = re.sub(r"@\d+", "@customer", text)
    # Normalize excessive whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def download_and_extract_applesupport(byte_range_mb: int = 40) -> List[Dict[str, Any]]:
    """Stream a subset of twcs.csv and filter for AppleSupport threads."""
    print(f"Streaming {byte_range_mb}MB of Customer Support on Twitter dataset...")
    bytes_to_read = byte_range_mb * 1024 * 1024
    
    req = urllib.request.Request(
        TWCS_URL, 
        headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes=0-{bytes_to_read}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw_bytes = resp.read()
            raw_text = raw_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Network error downloading dataset: {e}")
        return []

    print(f"Downloaded {len(raw_bytes)/(1024*1024):.2f} MB. Parsing CSV rows...")
    
    # Cache raw for reproducibility
    with open(RAW_CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(raw_text[:min(len(raw_text), 5000000)]) # cache preview
    
    reader = csv.DictReader(io.StringIO(raw_text))
    
    tweets_by_id = {}
    inbound_customer_tweets = []
    
    for row in reader:
        tid = row.get("tweet_id")
        if not tid:
            continue
        author = row.get("author_id") or ""
        inbound_val = row.get("inbound") or ""
        inbound = inbound_val.lower() == "true"
        text = row.get("text") or ""
        response_tweet_id = row.get("response_tweet_id") or ""
        in_response_to = row.get("in_response_to_tweet_id") or ""
        
        record = {
            "tweet_id": tid,
            "author_id": author,
            "inbound": inbound,
            "text": text,
            "response_tweet_id": response_tweet_id,
            "in_response_to_tweet_id": in_response_to,
            "created_at": row.get("created_at") or ""
        }
        tweets_by_id[tid] = record
        
        if author == "AppleSupport" or "@AppleSupport" in text or inbound:
            if inbound and "@AppleSupport" in text:
                inbound_customer_tweets.append(record)

    print(f"Total parsed tweets in buffer: {len(tweets_by_id):,}")
    print(f"Customer tweets targeting @AppleSupport: {len(inbound_customer_tweets):,}")

    dialogues = []
    
    for cust_tweet in inbound_customer_tweets:
        cust_id = cust_tweet["tweet_id"]
        cust_text = clean_tweet_text(cust_tweet["text"])
        
        # Check direct response
        resp_ids = cust_tweet.get("response_tweet_id", "").split(",")
        agent_reply_text = ""
        agent_tweet_id = ""
        
        for r_id in resp_ids:
            r_id = r_id.strip()
            if r_id in tweets_by_id and tweets_by_id[r_id]["author_id"] == "AppleSupport":
                agent_reply_text = clean_tweet_text(tweets_by_id[r_id]["text"])
                agent_tweet_id = r_id
                break
                
        if cust_text and len(cust_text) > 15:
            dialogue = {
                "dialogue_id": f"apple_{cust_id}",
                "customer_tweet_id": cust_id,
                "customer_text": cust_text,
                "agent_tweet_id": agent_tweet_id,
                "agent_reply": agent_reply_text,
                "has_agent_reply": bool(agent_reply_text),
                "created_at": cust_tweet.get("created_at", "")
            }
            dialogues.append(dialogue)

    print(f"Extracted {len(dialogues)} high-quality customer-brand dialogues.")
    
    # Save dialogues
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(dialogues, f, indent=2, ensure_ascii=False)
    print(f"Saved processed dialogues to {PROCESSED_FILE}")
    
    # Extract Knowledge Base historical resolutions
    kb_items = []
    for d in dialogues:
        if d["has_agent_reply"] and len(d["agent_reply"]) > 25:
            kb_items.append({
                "id": d["dialogue_id"],
                "customer_problem": d["customer_text"],
                "historical_resolution": d["agent_reply"]
            })
            
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb_items, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(kb_items)} historical resolution items to {KB_FILE}")
    
    return dialogues

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/knowledge_base", exist_ok=True)
    download_and_extract_applesupport(byte_range_mb=35)
