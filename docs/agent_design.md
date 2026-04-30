# Agent 设计说明

## 目标

这个项目不是普通问答机器人，而是一个面向数据分析岗位的 Agent 工作台：根据业务问题检索指标口径，选择数据源，生成只读 SQL，执行查询，输出表格、图表和中文分析结论。

## 工作流

1. Question router：根据问题关键词选择数据源。
2. RAG retriever：从内置指标字典检索相关口径。
3. SQL planner：使用 deterministic 模板生成只读 SQL。
4. SQL guardrail：拒绝写操作和多语句 SQL。
5. Query tool：执行 SQLite 查询。
6. Chart tool：根据结果生成基础图表。
7. Reporter：输出中文摘要和下一步建议。

## 数据源

- `connected_vehicle`：车主 App 生命周期增长项目。
- `benefit_ltv`：用车权益 LTV 与归因项目。
- `search_rank`：本地生活搜索排序 ML 项目。

## LLM 策略

默认使用 deterministic mock agent，保证 GitHub 复现不依赖 API key。存在 `OPENAI_API_KEY` 时，项目可扩展为真实 LLM planner，但安全边界仍由 SQL guardrail 控制。

## 安全边界

- 只允许 `SELECT` 和 `WITH` 查询。
- 拒绝 `DROP/DELETE/UPDATE/INSERT/ALTER/CREATE/ATTACH/DETACH/VACUUM`。
- 一次只允许一条 SQL。
- 默认只访问合成 SQLite 数据。
