# Agent 调度系统 v3.0 实施方案（最终版）

## 整合来源

- Gemini 3.0 Pro 审查报告
- Perplexity GPT-5.2 三段审查报告
- Kitt v2.0 测试经验

## 实施顺序（今晚完成）

### Phase 1: 数据契约层（基础）

1. AttemptResult / FailType / ModelProfile 数据类
2. schema_validate() 输出校验
3. classify_failure() 失败分类器

### Phase 2: 智能 Fallback

4. ELO 动态排序 elo_sorted_models()
5. smart_fallback() 逐级升级
6. 降级交付（部分结果复用）

### Phase 3: 质检升级

7. judge 统一输出（score 0-1 + blame_node + fix_instructions）
8. 定向重试（只重跑 blame_node）
9. rubric 按桶定制

### Phase 4: 路由升级

10. Triage v3（输出 sub_intent + op_type + complexity）
11. 二级子路由匹配
12. DAG 模板选择

### Phase 5: 并行 subagent

13. parallel_wave() asyncio 并行
14. merge_results() map-reduce 合并
15. 侦察任务并行化

---

**开始时间**: 2026-02-23 00:20
**目标**: 今晚完成 Phase 1-4，Phase 5 视时间决定
