# OpenClaw "眼睛"选型方案 v1.0

> 2026-03-27 | 厂长拍板定稿

---

## 1. 为什么选 agent-browser 做主刀

| 维度       | agent-browser                                    | browser-use                 | PinchTab              | OpenClaw 内置 browser        |
| ---------- | ------------------------------------------------ | --------------------------- | --------------------- | ---------------------------- |
| Token 消耗 | **~200 tokens/页**（快照只返回可交互元素语义树） | ~2000-5000（完整 DOM）      | ~800（text 模式）     | ~8000+（完整 snapshot）      |
| 速度       | **<0.5s**（Rust CLI）                            | 1-3s（Python + Playwright） | 0.5-1s                | 1-2s                         |
| CLI 适配   | ✅ 原生 CLI，exec 一条命令                       | ❌ Python 库，需包装        | ✅ CLI                | ❌ 需 browser tool JSON 调用 |
| 元素引用   | `@e1` `@e2` 语义 ref                             | CSS 选择器                  | `ref=1` 数字引用      | role-based ref               |
| 持久化登录 | ✅ Kernel 云浏览器                               | ✅ 内置                     | ❌ 无                 | ❌ 无                        |
| 反爬绕过   | ✅ Kernel stealth                                | ✅ 内置                     | ❌ 无                 | ❌ 无                        |
| 安装状态   | ✅ 已装 0.15.2                                   | ❌ 未装                     | ✅ 已装（服务不稳定） | ✅ 内置                      |

**结论**：agent-browser 在 token 效率和 CLI 适配性上碾压其他方案。AI Agent 场景下，token 就是钱，省 95% 就是省 95% 的成本。

## 2. 为什么 browser-use 只做备选

- **优势**：更智能（内置 LLM 规划）、复杂多步任务更可靠
- **劣势**：Python 依赖重、启动慢、token 消耗高、需要额外包装成 CLI
- **定位**：等一期跑通后，二期用于复杂网页交互（多步表单、动态页面、需要 LLM 判断的操作流）

## 3. OpenClaw 最佳实践

### 工具选择优先级（铁律）

```
1. API/CLI 原生工具（零浏览器开销）
2. agent-browser（轻量、省 token）
3. OpenClaw browser evaluate（页面已打开时的快速提取）
4. browser-use（复杂多步任务）
5. 手动操作（最后手段）
```

### agent-browser 在 OpenClaw 中的调用模式

```bash
# 模式 A：一次性抓取（最常用）
exec: agent-browser open <url> && agent-browser snapshot -i && agent-browser close

# 模式 B：交互操作（搜索/填表）
exec: agent-browser open <url>
exec: agent-browser snapshot -i          # 看页面结构
exec: agent-browser fill @e2 "关键词"     # 填表
exec: agent-browser click @e3            # 提交
exec: agent-browser snapshot -i          # 看结果
exec: agent-browser close

# 模式 C：截图取证
exec: agent-browser open <url> && agent-browser screenshot /tmp/page.png && agent-browser close

# 模式 D：页面文本提取
exec: agent-browser open <url>
exec: agent-browser get text @e1         # 提取指定元素文本
exec: agent-browser eval "document.querySelector('.content').textContent"  # 自由提取
exec: agent-browser close
```

### 登录态管理

```bash
# 方案 A：本地 Chromium（免费，适合不需反爬的站点）
agent-browser open https://gemini.google.com  # 首次手动登录
# 后续复用同一浏览器实例

# 方案 B：Kernel 云浏览器（付费，适合需要反爬+持久化的站点）
export KERNEL_API_KEY="xxx"
export KERNEL_PROFILE_NAME="gemini-session"
export KERNEL_STEALTH=true
agent-browser -p kernel open https://gemini.google.com
```

### 失败降级链路

```
agent-browser 超时/失败
  → 重试 1 次（换 --headed 模式）
  → OpenClaw browser evaluate（如果页面已在 OpenClaw 浏览器中打开）
  → web_fetch（简单页面、无 Cloudflare 防护）
  → 报告厂长，人工介入
```

---

## 4. 抖音工作流接入方案

### 当前架构

```
用户输入 → FastAPI (8765)
         → 热榜分析 (step2)
         → 话题生成 (step3)
         → 脚本生成 (step4)
         → 前端展示
```

### 一期接入：网页出图链路

```
脚本生成完成后 → 提取关键画面描述
              → agent-browser 打开 Gemini 网页版
              → 自动填入图片 prompt
              → 等待生成 → 截图/下载
              → 存入 task 的 img_files 字段
              → 前端展示配图
```

**具体实现**：

```bash
# 1. 打开 Gemini（首次需手动登录，后续复用）
agent-browser open https://gemini.google.com/app

# 2. 找到输入框
agent-browser snapshot -i

# 3. 填入图片 prompt
agent-browser fill @eN "生成一张振动刀切割皮革的工厂场景图，工业风格..."

# 4. 提交
agent-browser press Enter

# 5. 等待生成（轮询快照直到出现图片）
sleep 10 && agent-browser snapshot -i

# 6. 找到图片元素，截图保存
agent-browser screenshot /Users/apple/dyproject/output/img_xxx.png

# 7. 或直接下载图片
agent-browser eval "document.querySelector('img.generated').src"
```

### 登录态复用策略

| 站点       | 登录方式    | 复用策略                                  |
| ---------- | ----------- | ----------------------------------------- |
| Gemini     | Google 账号 | 本地 Chromium，首次手动登录，后续自动复用 |
| 豆包       | 字节账号    | 同上                                      |
| Midjourney | Discord     | Kernel 云浏览器（需持久化 Discord 登录）  |

### 失败降级路径

```
Gemini 网页出图
  → 失败？→ 豆包网页出图
  → 失败？→ OpenClaw image_generate API（可能 429）
  → 失败？→ 跳过图片，只输出脚本（降级不阻断）
```

### API 新增（app_http.py 需要的改动）

```python
# POST /api/tasks/{task_id}/generate-images
# 触发 agent-browser 为指定任务生成配图
# 返回：{ ok: true, images: ["path1.png", "path2.png"] }

# GET /api/tasks/{task_id}/images
# 返回任务的所有配图路径
```

---

## 5. 二期规划（暂不实施）

- 补 browser-use，用于复杂多步网页任务
- Sora/Runway 视频生成接入
- 一键发布到抖音（需要研究抖音创作者 API）
- TTS 配音接入
