# 计划书：defensive-refusal-bench-zh
## 中文网安「防御问题误拒」评测基准（over-refusal，可机器评分）

测安全对齐模型是否把**正当防御/安全教育问题**也误拒，并以**真实危害请求**作对照防止刷分。

- v0：72 条（56 should_answer 从 cybersec-qa-dataset-zh 语料挖掘 + 16 should_refuse 人工对照）。目标扩至 300+。
- 指标：**false_refusal_rate**（越低越好）、helpfulness_on_legit、**harmful_refusal_rate**（越高越好）、safety_utility_gap。
- 与 [agent-safety-bench-zh](https://github.com/uninhibited-scholar/agent-safety-bench-zh) 互补：那个测"该拦的拦没拦住"，本基准测"不该拒的有没误拒"——合起来覆盖安全模型"安全 × 可用"两条边。
- 红线：should_refuse 样本**只描述请求、不含可运行攻击载荷**；should_answer 只收"问原理/防御"的教育性问题。
- 扩量：从语料继续挖更多边界问法；引入真实模型预测（用 scripts/refusal_detect.py 把模型回复转 action）跑多模型排行榜。
