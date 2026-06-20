#!/usr/bin/env python3
"""Naive keyword-safety baseline: refuse any question containing a 'scary' cue.
Demonstrates the over-refusal failure mode this benchmark targets."""
import json,os,re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUES=["注入","提权","绕过","利用","payload","exploit","shellcode","木马","后门","勒索",
 "免杀","爆破","嗅探","中间人","溢出","反序列化","横向移动","钓鱼","社工","DDoS","XSS",
 "CSRF","SSRF","加壳","逆向","破解","攻击","漏洞","劫持","投毒","越权","哈希","入侵","盗"]
rx=re.compile("|".join(map(re.escape,CUES)))
out=os.path.join(ROOT,"baselines","predictions_keyword_guard.jsonl")
with open(out,"w",encoding="utf-8") as w:
    for l in open(os.path.join(ROOT,"data","bench.jsonl"),encoding="utf-8"):
        l=l.strip()
        if not l:continue
        o=json.loads(l)
        act="refuse" if rx.search(o["question"]) else "answer"
        w.write(json.dumps({"id":o["id"],"action":act},ensure_ascii=False)+"\n")
print("wrote",out)
