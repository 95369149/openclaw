# Agent 结构化交接协议 v1.0

> 解决 Agent 之间靠自然语言传递数据导致的解析错误、信息丢失问题

## 核心原则

- **机器可读优先**：Agent 输出必须是结构化 JSON，不是散文
- **版本控制**：每个 manifest 带版本号，便于兼容升级
- **最小上下文**：只传下游需要的数据，不传全文

---

## 标准 Manifest 格式

```json
{
  "version": "1.0",
  "produced_by": "agent_id",
  "produced_at": "2026-04-22T14:30:00+08:00",
  "task_id": "task_label",
  "content_type": "research|analysis|draft|review|data",
  
  "summary": {
    "status": "success|partial|failed",
    "key_findings": ["要点1", "要点2"],
    "confidence": 0.85
  },
  
  "payload": {
    // 根据 content_type 变化
  },
  
  "next_actions": [
    {"agent": "reviewer", "task": "审核", "priority": 1}
  ],
  
  "metadata": {
    "tokens_used": 1500,
    "sources": ["url1", "url2"],
    "warnings": []
  }
}
```

---

## 各类型 Payload 定义

### research（调研类）
```json
"payload": {
  "query": "原始问题",
  "sources": [
    {"title": "", "url": "", "relevance": 0.9, "key_points": []}
  ],
  "answer": "综合答案"
}
```

### analysis（分析类）
```json
"payload": {
  "input_summary": "输入摘要",
  "framework": "分析框架",
  "conclusions": [{"point": "", "evidence": "", "confidence": 0.8}],
  "recommendations": []
}
```

### draft（起草类）
```json
"payload": {
  "doc_type": "article|email|report",
  "title": "",
  "content": "",
  "word_count": 500,
  "sections": [{"heading": "", "content": ""}]
}
```

### review（审核类）
```json
"payload": {
  "target_task_id": "被审核的任务ID",
  "score": 8.5,
  "issues": [{"severity": "high|medium|low", "description": ""}],
  "suggestions": [],
  "pass": true
}
```

---

## 使用规范

### 写入位置
```
memory/shared/YYYY-MM-DD_<agentId>_<taskId>_manifest.json
```

### Jimmy 派发并行任务示例
```python
tasks = [
    {
        "agentId": "scout",
        "task": "调研竞品A，输出 manifest 到 shared/scout_a_manifest.json",
        "label": "research_a"
    },
    {
        "agentId": "scout", 
        "task": "调研竞品B，输出 manifest 到 shared/scout_b_manifest.json",
        "label": "research_b"
    }
]
# 并行派发
results = parallel_spawn(tasks)
# 读取所有 manifest 汇总
manifests = [read_json(f) for f in results.output_files if f.endswith('_manifest.json')]
```

### 子 Agent 必须遵守
1. 输出文件必须以 `_manifest.json` 结尾
2. 必须包含 `version` 和 `produced_by` 字段
3. `summary.status` 必须明确标记成功/失败
4. 失败时必须写 `metadata.warnings` 说明原因

---

## 验收标准

- [ ] 所有子 Agent 输出改为 manifest JSON 格式
- [ ] Jimmy 并行派发工具上线
- [ ] 汇总 Agent 能正确解析多个 manifest
- [ ] 失败时能定位到具体 Agent 和环节
