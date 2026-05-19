# 数据分析 Agent 评测报告

- 问题数：32
- 成功率：100.0%
- 数据源路由准确率：100.0%
- 指标口径检索命中率：100.0%
- SQL 可执行率：100.0%
- 危险 SQL 拒绝率：100.0%

## 关于 100% 通过率

本项目默认使用 **deterministic mock agent**（确定性模板匹配），而非概率型 LLM。32 道评测题覆盖了模板中的所有路径分支，因此四个维度均达到 100%。

这不是靠"运气好"——而是靠"设计完整"。mock agent 的本质是：把业务问题 → SQL 的映射编码为确定性规则。评测集的作用是验证这些规则是否覆盖了预期场景。

如果接入真实 LLM（设置 `OPENAI_API_KEY`），成功率预计会降到 85%-95%，但这反映的是 LLM 的不确定性，而非评测框架的问题。安全边界（SQL guardrail）在任何模式下都由代码控制，不会因 LLM 而失效。

## 评测维度说明

| 维度 | 含义 | 为什么重要 |
| --- | --- | --- |
| 数据源路由准确率 | Agent 是否把问题路由到正确的数据源（benefit_ltv / search_rank / connected_vehicle） | 路由错误会导致后续所有步骤无效 |
| 指标口径命中率 | RAG 检索是否找到了对应业务场景的指标定义 | 口径错误会导致 SQL 逻辑正确但结果无业务意义 |
| SQL 可执行率 | 生成的 SQL 在 SQLite 中能否正常执行并返回结果 | 可执行是基础门槛，无法执行意味着 Agent 不可用 |
| 危险 SQL 拒绝率 | 对 DROP/UPDATE/DELETE 等写操作是否全部拦截 | 安全边界，生产环境中至关重要 |

## 评测详细结果

| id | source | success | error |
| --- | --- | --- | --- |
| q01 | benefit_ltv | True |  |
| q02 | benefit_ltv | True |  |
| q03 | benefit_ltv | True |  |
| q04 | benefit_ltv | True |  |
| q05 | benefit_ltv | True |  |
| q06 | benefit_ltv | True |  |
| q07 | benefit_ltv | True |  |
| q08 | benefit_ltv | True |  |
| q09 | search_rank | True |  |
| q10 | search_rank | True |  |
| q11 | search_rank | True |  |
| q12 | search_rank | True |  |
| q13 | search_rank | True |  |
| q14 | search_rank | True |  |
| q15 | search_rank | True |  |
| q16 | search_rank | True |  |
| q17 | connected_vehicle | True |  |
| q18 | connected_vehicle | True |  |
| q19 | connected_vehicle | True |  |
| q20 | connected_vehicle | True |  |
| q21 | connected_vehicle | True |  |
| q22 | connected_vehicle | True |  |
| q23 | connected_vehicle | True |  |
| q24 | connected_vehicle | True |  |
| q25 | benefit_ltv | True |  |
| q26 | benefit_ltv | True |  |
| q27 | search_rank | True |  |
| q28 | search_rank | True |  |
| q29 | connected_vehicle | True |  |
| q30 | connected_vehicle | True |  |
| q31 | benefit_ltv | True |  |
| q32 | search_rank | True |  |
