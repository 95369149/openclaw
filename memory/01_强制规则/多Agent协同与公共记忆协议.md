# 多 Agent 协同与公共记忆协议 v1.0
> 解决多并发、状态覆盖、失忆等协同漏洞的底层法则。所有 Agent 必须严格遵守。

## 1. 读写权限隔离规则

为防止系统核心配置被篡改或覆盖，各 Agent 权限作如下隔离：

| Agent | `openclaw.json` / 系统环境 | `task-board.json` (任务板) | `memory/shared/` (共享记忆) | 核心规则文档 (`01_强制规则/`) |
|-------|--------------------------|--------------------------|-----------------------------|------------------------------|
| **jimmy** (L0 中枢) | 读 + 写 (必须走 patch) | 读 + 写 (唯一统筹者) | 读 + 归档/清理 | 读 + 写 (唯一修订者) |
| **deep** (L1 主力) | 仅读 (只读不可写) | 仅读 (拉取任务状态) | 读 + 写 (强制作业留痕) | 仅读 |
| **main** (L1 多模态)| 仅读 | 仅读 | 读 + 写 (强制作业留痕) | 仅读 |
| **logic** (L1 推理) | 仅读 | 仅读 | 读 + 写 (强制作业留痕) | 仅读 |
| **kitt** (L2 决策) | 仅读 | 仅读 | 读 + 写 (提议与决策) | 仅读 |

> **⚠️ 铁律**：除了 Jimmy，其他所有子 Agent **绝对禁止**使用 `sed`/`edit`/`write` 修改 `openclaw.json` 或 `task-board.json`。若需修改状态，必须将变更意图写入 `memory/shared/`，由 Jimmy 验收并代为更新。

## 2. 公共记忆交互标准 (SOP)

### A. 子 Agent 唤醒后的第一动作（Read）
所有子 Agent 收到派发任务后，**执行任何操作前**，必须先执行以下命令以建立上下文：
```bash
1. cat /Users/apple/.openclaw/workspace/memory/task-board.json
2. ls -t /Users/apple/.openclaw/workspace/memory/shared/ | head -n 5
```
*如果不读上下文就开始干活，属于严重违规，会导致重复劳动。*

### B. 任务执行中的留痕（Stream-Write）
不要等任务全部做完再写文件！一旦任务执行超过 2 个步骤，或者获得了关键信息，必须立即追加写入文件。
*方法：使用 `write` 或 `edit` 工具，将中间态内容写入 `/Users/apple/.openclaw/workspace/memory/shared/YYYY-MM-DD_<agentName>_<任务简称>.md`。*

### C. 任务完成后的闭环（Write & Verify）
任务执行完毕，子 Agent 必须完成以下两步才能宣告结束：
1. **写总结**：在所属的 shared 文件末尾写入明确的【执行结论】和【待跟进项】。
2. **写后即验**：必须调用 `read` 工具读取自己刚写的文件，或者调用 `scripts/qmd-verify.sh <关键词>` 确认文件已真实落盘且被系统索引。
*如果写了文件但不验证，视同任务未完成。*

## 3. 并发防冲突机制

- **命名空间隔离**：子 Agent 写 `shared/` 文件时，文件名必须包含自己的专属前缀（如 `deep_`、`main_`），**绝对禁止**两个 Agent 同时修改同一个 `.md` 文件。
- **状态同步流**：
  1. `deep` 执行完成 -> 写入 `deep_xxx.md`
  2. `deep` 退出并自动通知 `jimmy`
  3. `jimmy` 读取 `deep_xxx.md`
  4. `jimmy` 修改 `task-board.json` 状态为 done

此协议旨在彻底杜绝“盲目覆盖”、“上下文漂移”与“写文件失败”三大漏洞。