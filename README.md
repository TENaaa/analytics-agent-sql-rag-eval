# 指标字典驱动的 Web 数据分析 Agent 与评测框架

这是一个 AI Agent 方向的数据分析作品集项目。Agent 接入前三个合成数据项目的 SQLite，根据自然语言问题检索指标口径、生成只读 SQL、执行查询、生成表格/图表，并输出中文分析结论。

项目默认使用 deterministic mock agent，不依赖线上大模型 API；如果存在 `OPENAI_API_KEY`，可以扩展接入真实 LLM planner。公开仓库只使用合成数据项目产物，不包含内部资料或个人信息。

## 运行

先确保前三个项目已生成 SQLite：

```bash
cd ../connected-vehicle-app-growth-analytics && python3 -m cv_growth run-all
cd ../growth-incrementality-ltv-attribution && python3 -m growth_ltv run-all
cd ../local-life-search-ranking-ml-lab && python3 -m search_rank_ml run-all
```

安装依赖并启动 Web：

```bash
python3 -m pip install -r requirements.txt
python3 -m analytics_agent run-web
```

浏览器访问：

```text
http://127.0.0.1:8008
```

CLI 示例：

```bash
python3 -m analytics_agent ask "哪个渠道毛利ROAS最高？"
python3 -m analytics_agent eval
python3 -m analytics_agent export-report
```

## 项目亮点

- Web 页面完成“提问 -> SQL -> 表格 -> 图表 -> 中文结论”闭环。
- 默认无 API key 可复现，适合 GitHub 展示和面试现场运行。
- 跨 3 个项目数据源，不混淆指标口径。
- 内置 SQL 安全网关，拒绝危险写操作。
- 自带评测集，输出 SQL 可执行率、数据源路由准确率、指标口径命中率和安全拒绝率。

## 验证

```bash
PYTHONPYCACHEPREFIX=/tmp/analytics_agent_pycache python3 -m compileall .
python3 tests/smoke_test.py
```

## 关键产物

- `docs/agent_design.md`：Agent 架构与安全边界
- `reports/agent_eval_report.md`：评测报告
- `eval/questions.json`：评测问题集
- `web/`：FastAPI + 原生前端

## License

MIT
