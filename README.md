# defensive-refusal-bench-zh

中文网安「防御问题误拒」评测基准（over-refusal · 可机器评分 · 防御导向）。

[![CI](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh/actions/workflows/validate.yml/badge.svg)](https://github.com/uninhibited-scholar/defensive-refusal-bench-zh/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

测一个安全对齐的模型，会不会把**正当的防御/安全教育问题**（"SQL 注入的原理是什么"、"如何检测横向移动"）也一并**误拒**——这会让 AI 对真正做防御的人变得没用。用**真实危害请求**作对照组，防止"全部作答"刷分。

## 为什么需要它
"攻防同源"使安全问题天然 dual-use，安全对齐很容易**矫枉过正、误伤防御方**。该问题在英文刚被确立（[Defensive Refusal Bias, ICLR 2026](https://arxiv.org/html/2603.01246v1)；OR-Bench/XSTest/FORTRESS），**中文安全垂类仍空白**（[CSSBench](https://arxiv.org/html/2601.00588) 只做通用误拒）。详见 [docs/prior-art.md](docs/prior-art.md)。

它与 [agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) 互补——那个测"**该拦的拦没拦住**"，本基准测"**不该拒的有没误拒**"，合起来覆盖安全模型 **安全 × 可用** 两条边。

## 数据
- `data/bench.jsonl`，v0.2 共 **134 条**：112 `should_answer`（从 [cybersec-qa-dataset-zh](https://github.com/uninhibited-scholar/cybersec-qa-dataset-zh) 语料挖掘的边界问题，7 主题）+ 22 `should_refuse`（人工对照，面向真实目标的实施性危害请求）。
- 字段：`id, label, category, difficulty, question, gold{action}, why, surface_cues, tags`。详见 [docs/taxonomy.md](docs/taxonomy.md)。

## 评测
让模型回答每条 `question`，把回复经 `scripts/refusal_detect.py` 判为 `answer/refuse`（或直接给 `{id,action}`），再：
```bash
python3 scripts/score.py your_predictions.jsonl
```

## 基线：朴素关键词护栏
"命中危险词就拒答"这种朴素安全策略，跑本基准结果：
```json
{
  "missing": 0,
  "false_refusal_rate": 1.0,
  "helpfulness_on_legit": 0.0,
  "harmful_refusal_rate": 0.682,
  "safety_utility_gap": 0.682
}
```
**看点**：它**误拒了 100% 的正当防御问题**（false_refusal_rate = 1.0），却**仍漏过约 32% 的真实危害请求**（harmful_refusal_rate ≈ 0.68）。一句话——**关键词过滤分不清"讲原理"和"搞破坏"，只会一边误伤防御者、一边放过真坏人。** 这正是需要专门评测、并做更细对齐的理由。

## 质量保证
`scripts/check_bench.py` + CI 每次提交校验 schema、约束（label↔action）、去重、配比、纯净度。**禁止靠删样本或翻转标签骗过校验。**

## 诚实说明
v0.2、134 条、单人构建、规则基线——**能跑通、有论点、可复现**的早期基准；should_answer 来自既有公开语料的边界问法，should_refuse 为人工编写且**只描述请求、不含可运行攻击载荷**。扩量与多模型排行榜见 [PLAN.md](PLAN.md)。许可 CC BY 4.0。
