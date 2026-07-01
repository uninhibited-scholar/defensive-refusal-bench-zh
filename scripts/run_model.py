#!/usr/bin/env python3
"""Run an OpenAI-compatible model over defensive-refusal-bench-zh.
Asks the question, captures response, then refusal_detect.py classifies it.

Usage:
  export OPENAI_API_KEY=...
  python3 scripts/run_model.py --model <name> [--base-url <url>] [--limit N]
Output: predictions_<model>.jsonl  ({"id":..., "action":"answer|refuse"})
"""
import argparse, json, os, re, ssl, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from refusal_detect import is_refusal
try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def call(base, key, model, q):
    body = json.dumps({"model":model,"temperature":0,"max_tokens":500,
        "messages":[{"role":"user","content":q}]}).encode()
    req = urllib.request.Request(base.rstrip("/")+"/chat/completions", data=body,
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    for _r in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120, context=_SSL) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception:
            import time; time.sleep(2*(_r+1))
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL","https://api.openai.com/v1"))
    ap.add_argument("--key", default=os.environ.get("OPENAI_API_KEY",""))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if not a.key: print("ERROR: set OPENAI_API_KEY"); return 2
    out = a.out or os.path.join(ROOT, f"predictions_{re.sub(r'[^a-zA-Z0-9._-]','_',a.model)}.jsonl")
    rows = [json.loads(l) for l in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8") if l.strip()]
    if a.limit: rows = rows[:a.limit]
    done=set()
    if os.path.exists(out):
        for l in open(out,encoding="utf-8"):
            if l.strip():
                try: done.add(json.loads(l)["id"])
                except: pass
    todo=[o for o in rows if o["id"] not in done]
    print(f"resume: {len(done)} done, {len(todo)} todo")
    with open(out,"a",encoding="utf-8") as w:
        for i,o in enumerate(todo,1):
            for _r in range(3):
                resp = call(a.base_url,a.key,a.model,o["question"])
                if resp: break
            action = "refuse" if is_refusal(resp) else "answer"
            w.write(json.dumps({"id":o["id"],"action":action},ensure_ascii=False)+"\n"); w.flush()
            print(f"  [{i}/{len(todo)}] {o['id']} -> {action}")
    print(f"\nwrote {out}")
if __name__=="__main__": sys.exit(main())
