---
name: skill-standard
version: 1.0.0
description: |
  Kitt 系统 Skill 标准格式定义。所有新建/改造的 skill 必须符合此标准。
---

# Skill 标准格式

## 文件结构

```
skills/{skill-name}/
├── SKILL.md          # 主文件（必须）
├── routing-eval.jsonl # 路由测试用例（可选）
└── templates/        # 模板文件（可选）
```

## SKILL.md 必须包含

### 1. YAML Frontmatter（必须）

```yaml
---
name: { skill-name }
version: 1.0.0
description: |
  一段话描述这个 skill 做什么、什么时候用。
triggers:
  - "{触发短语 1}"
  - "{触发短语 2}"
tools:
  - { tool1 }
  - { tool2 }
agent: { 推荐执行 agent: deep/main/kitt/sino/scout/guard }
mutating: { true|false } # 是否会修改文件/状态
---
```

### 2. Contract（必须）

这个 skill 保证什么——3-5 条 bullet：

- 输入是什么
- 输出是什么
- 质量标准是什么
- 失败时怎么处理

### 3. Phases（必须）

编号的执行步骤。每步明确：

1. 做什么
2. 用什么工具
3. 输出什么
4. 下一步的判断条件

### 4. Output Format（必须）

好的输出长什么样。给一个真实例子或模板。

### 5. Anti-Patterns（必须）

3-5 条"不要做"，每条配"要做"：

- ❌ 不要 XXX → ✅ 要 YYY

### 6. Chaining（可选）

这个 skill 可以和哪些 skill 串联：

- 前置：执行本 skill 前通常先跑什么
- 后置：执行完后通常接什么

## 命名规范

- 目录名：小写 kebab-case（`notebooklm-content-factory`）
- 文件名：`SKILL.md`（大写）
- 触发词：用户自然语言（中英文都写）

## MECE 检查

创建新 skill 前必须：

1. 查 `skills/RESOLVER.md` 有没有已覆盖的 skill
2. 如果有重叠 → 扩展已有 skill，不新建
3. 如果确实是新能力 → 创建后更新 RESOLVER.md

## 质量门禁

- 新 skill 必须经 jimmy 或 kitt 审核
- 改造后的 skill 必须实际跑一次验证
- 不符合标准的 skill 不进 RESOLVER.md
