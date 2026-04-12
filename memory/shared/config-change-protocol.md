# 配置变更协议 v1.0

> 2026-02-28 by jimmy

## 规则

子 agent 不能直接修改 openclaw.json 或重启 gateway。

如需配置变更，子 agent 写入以下格式到 `memory/shared/pending-config-<日期>_<agent>_<简述>.md`：

```
## 建议配置变更
- 变更内容：（JSON diff 或描述）
- 原因：（为什么要改）
- 风险：low/medium/high
- 紧急度：立即/下次心跳/不急
```

## 执行流程

1. 子 agent 写入 pending-config 文件
2. jimmy 心跳或下次活跃时检查 `ls memory/shared/pending-config-*`
3. jimmy 验证合理性 → 展示给厂长确认 → 执行
4. 执行后删除 pending 文件，结果写入当日日志

## 禁止

- 子 agent 直接 exec 修改 openclaw.json
- 子 agent 调用 gateway restart
- 跳过厂长确认的"紧急修复"
