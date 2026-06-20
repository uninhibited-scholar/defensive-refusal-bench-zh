#!/usr/bin/env python3
import json,os,re,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data","bench.jsonl")
KEYS={"id","label","category","difficulty","question","gold","why","surface_cues","tags"}
LAB={"should_answer","should_refuse"}; ACT={"answer","refuse"}; DIFF={"easy","medium","hard"}
DIRTY=[re.compile(p) for p in [r"APT\s*\d+",r"(俄罗斯|朝鲜|伊朗)\s*(黑客|组织|情报)",r"地缘政治",r"Lazarus\s*Group"]]
def main():
    rows=[];prob=[]
    for ln,line in enumerate(open(DATA,encoding="utf-8"),1):
        line=line.strip()
        if not line:continue
        try:o=json.loads(line)
        except Exception as e:prob.append(f"L{ln} bad json {e}");continue
        rows.append(o)
        if set(o)!=KEYS:prob.append(f"{o.get('id')} keys {sorted(o)}")
        if o.get("label") not in LAB:prob.append(f"{o.get('id')} bad label")
        if o.get("difficulty") not in DIFF:prob.append(f"{o.get('id')} bad difficulty")
        if o.get("gold",{}).get("action") not in ACT:prob.append(f"{o.get('id')} bad action")
        if o.get("label")=="should_answer" and o["gold"]["action"]!="answer":prob.append(f"{o.get('id')} answer-constraint")
        if o.get("label")=="should_refuse" and o["gold"]["action"]!="refuse":prob.append(f"{o.get('id')} refuse-constraint")
        if len(str(o.get("why","")))<10:prob.append(f"{o.get('id')} why too short")
        if not str(o.get("question","")).strip():prob.append(f"{o.get('id')} empty question")
        b=json.dumps(o,ensure_ascii=False)
        for r in DIRTY:
            if r.search(b):prob.append(f"{o.get('id')} purity: {r.pattern}")
    ids=[r["id"] for r in rows]
    if len(ids)!=len(set(ids)):prob.append("dup id")
    qq=[r["question"] for r in rows]
    if len(qq)!=len(set(qq)):prob.append("dup question")
    from collections import Counter
    c=Counter(r["label"] for r in rows);n=len(rows) or 1
    if not(0.50<=c["should_answer"]/n<=0.90):prob.append(f"answer ratio {c['should_answer']/n:.0%}")
    if c["should_refuse"]<8:prob.append("too few should_refuse controls")
    print(f"checked {len(rows)} | {dict(c)}")
    if prob:
        print(f"\nFAIL — {len(prob)}:");[print("  -",p) for p in prob[:50]]
        print("\nFix the real gap; do NOT pass by deleting samples or flipping labels.");return 1
    print("PASS — schema ok, constraints hold, unique, ratio ok, purity clean.");return 0
if __name__=="__main__":sys.exit(main())
