# 指标字典驱动的 Web 数据分析 Agent 与评测框架

这是一个 AI Agent 方向的数据分析作品集项目。Agent 接入三个合成数据项目的 SQLite，根据自然语言问题检索指标口径、生成只读 SQL、执行查询、生成表格/图表，并输出中文分析结论。

项目默认使用 deterministic mock agent，不依赖线上大模型 API；如果存在 `OPENAI_API_KEY`，可以扩展接入真实 LLM planner。公开仓库只使用合成数据项目产物，不包含内部资料或个人信息。

## 30 秒速览

- **七步流水线**：提问 → 路由 → RAG检索 → SQL生成 → 安全校验 → 执行 → 图表→结论
- **三数据源协同**：车主增长 + 用车权益LTV + 本地生活搜索排序
- **四维自动评测**：数据源路由 100% · 指标口径 100% · SQL可执行 100% · 安全拒绝 100%
- **双模式交互**：Web 界面（一键启动）+ CLI 命令行
- **零 API Key 可复现**：默认 deterministic mock agent，clone 即跑

## 运行

### 前提：确保数据源 SQLite 已生成

Agent 需要三个上游项目的 SQLite 数据库。先进入对应目录执行一键命令：

```bash
# 在 connected-vehicle-app-growth-analytics 目录下
python3 -m cv_growth run-all

# 在 growth-incrementality-ltv-attribution 目录下
python3 -m growth_ltv run-all

# 在 local-life-search-ranking-ml-lab 目录下
python3 -m search_rank_ml run-all
```

> 提示：Agent 会检测数据源是否可用。如果某个 SQLite 不存在，Web 界面会显示「缺少 SQLite」，对应问题会返回友好提示。

### 安装依赖并启动 Web

```bash
python3 -m pip install -r requirements.txt
python3 -m analytics_agent run-web
```

浏览器访问：

```text
http://127.0.0.1:8008
```

### CLI 示例

```bash
# 单次提问
python3 -m analytics_agent ask "哪个渠道毛利ROAS最高？"

# 运行评测
python3 -m analytics_agent eval

# 导出评测报告
python3 -m analytics_agent export-report
```

## 架构设计

```
用户提问
  │
  ▼
Question Router ──→ 数据源路由（benefit_ltv / search_rank / connected_vehicle）
  │
  ▼
RAG Retriever ──→ 检索指标口径（4条knowledge base，可扩展）
  │
  ▼
SQL Planner ──→ 生成只读 SQL（mock模板 / 可选LLM）
  │
  ▼
SQL Guardrail ──→ 安全校验（拒绝写操作、多语句、危险token）
  │
  ▼
Query Tool ──→ SQLite 执行查询
  │
  ├──→ Chart Tool ──→ 自动生成 Matplotlib 图表
  │
  └──→ Reporter ──→ 中文分析结论 + 下一步建议
```

## 为什么要 deterministic mock agent

这是一个**有意的设计选择**，不是偷懒：

1. **可复现**：面试官 clone 下来就能跑，不需要 API key
2. **稳定评测**：32 题评测集每次结果一致，不是"运气好"
3. **安全可控**：SQL guardrail 由代码保证，不依赖 LLM 的"自律"
4. **可升级**：设置 `OPENAI_API_KEY` 环境变量即可切换到真实 LLM，安全边界不变

## 项目亮点

- Web 页面完成"提问 → SQL → 表格 → 图表 → 中文结论"闭环
- 默认无 API key 可复现，适合 GitHub 展示和面试现场运行
- 跨 3 个项目数据源，不混淆指标口径
- 内置 SQL 安全网关，拒绝危险写操作
- 自带 32 题评测集，输出四维指标

## 验证

```bash
PYTHONPYCACHEPREFIX=/tmp/analytics_agent_pycache python3 -m compileall .
python3 tests/smoke_test.py
```

## 关键产物

- `INTERVIEW_TALK_TRACK.md`：面试 3 分钟 / 8 分钟讲稿 + Q&A 预判
- `docs/agent_design.md`：Agent 架构与安全边界
- `reports/agent_eval_report.md`：评测报告（含维度说明）
- `eval/questions.json`：32 题评测集
- `web/`：FastAPI + 原生前端

## License

MIT
