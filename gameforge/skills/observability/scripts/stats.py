#!/usr/bin/env python3
"""
Observability — LLM usage stats for GameForge
Usage: stats.py today|week|top|all
"""
import sys, os, json, glob
from datetime import datetime, timedelta

LOGS_DIR = "/root/.openclaw/workspace/hooks/logs"

# Model pricing per 1M tokens (input/output) in USD
MODEL_PRICES = {
    "minimax":         {"in": 0.20, "out": 1.10},
    "minimax-text-01": {"in": 0.20, "out": 1.10},
    "claude-3-haiku":  {"in": 0.25, "out": 1.25},
    "claude-3-sonnet": {"in": 3.00, "out": 15.0},
    "gpt-4o-mini":     {"in": 0.15, "out": 0.60},
    "default":         {"in": 0.50, "out": 1.50},
}

def get_price(model, tokens_in, tokens_out):
    key = "default"
    for k in MODEL_PRICES:
        if k in model.lower():
            key = k; break
    p = MODEL_PRICES[key]
    return (tokens_in * p["in"] + tokens_out * p["out"]) / 1_000_000

def load_entries(days=1):
    entries = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = f"{LOGS_DIR}/llm-usage-{date}.jsonl"
        if os.path.exists(path):
            for line in open(path):
                if line.strip():
                    try: entries.append(json.loads(line))
                    except: pass
    return entries

def print_stats(entries, label):
    if not entries:
        print(f"No data for {label}"); return
    total_in  = sum(e.get("tokens_in", 0)  for e in entries)
    total_out = sum(e.get("tokens_out", 0) for e in entries)
    total_tok = sum(e.get("tokens_total", 0) for e in entries)
    success   = sum(1 for e in entries if e.get("success"))
    total_cost = sum(get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0)) for e in entries)
    avg_time  = sum(e.get("duration_sec", 0) for e in entries) / len(entries)

    print(f"\n{'='*50}")
    print(f"  GameForge Observability — {label}")
    print(f"{'='*50}")
    print(f"  Requests:     {len(entries)} total | {success} OK | {len(entries)-success} failed")
    print(f"  Tokens:       {total_in:,} in + {total_out:,} out = {total_tok:,} total")
    print(f"  Cost:         ${total_cost:.4f} USD")
    print(f"  Avg time:     {avg_time:.1f} sec/game")
    print(f"  Cost/game:    ${total_cost/len(entries):.4f} USD avg")
    models = list(set(e.get("model","?") for e in entries))
    print(f"  Models:       {', '.join(models)}")
    print(f"{'='*50}\n")

def cmd_today():
    print_stats(load_entries(1), "Today")

def cmd_week():
    print_stats(load_entries(7), "Last 7 days")

def cmd_top():
    entries = load_entries(30)
    by_cost = sorted(entries, key=lambda e: get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0)), reverse=True)
    print("\n  Top 5 most expensive generations:")
    for e in by_cost[:5]:
        cost = get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0))
        print(f"    {e.get('slug','?')} | {e.get('tokens_total',0):,} tokens | ${cost:.4f} | {e.get('duration_sec',0):.1f}s")

cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
if cmd == "today": cmd_today()
elif cmd == "week": cmd_week()
elif cmd == "top":  cmd_top()
elif cmd == "all":
    cmd_today(); cmd_week(); cmd_top()
else: print(__doc__)
