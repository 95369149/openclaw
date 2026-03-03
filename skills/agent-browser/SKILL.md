---
name: agent-browser
description: >
  Vercel Labs 的 AI Agent 专用浏览器自动化工具。Token 节省 95%+，速度提升 50%。
  使用场景：需要极致 Token 优化的浏览器操作、云端浏览器、持久化登录。
  触发词：浏览器自动化、网页抓取、持久化登录、Token 优化。
---

# agent-browser

Vercel Labs 开发的专为 AI Agent 设计的无头浏览器自动化 CLI 工具。

## 核心优势

1. **Token 节省 95%+**：采用"快照 + @ref 引用"机制，只返回可交互元素的语义树
2. **速度提升 50%**：Rust 原生 CLI，解析开销 <1ms
3. **AI 友好**：直接用 `@e1`、`@e2` 引用元素，不需要写 CSS 选择器
4. **云端集成**：支持 Browser Use Cloud 和 Kernel（持久化登录、绕过反爬虫）

## 安装

### 全局安装（推荐）
```bash
npm install -g agent-browser
agent-browser install  # 下载 Chromium
```

### 验证安装
```bash
agent-browser --version
# 输出：agent-browser 0.15.2
```

## 基础用法

### 1. 打开网页
```bash
agent-browser open <url>
```

### 2. 获取快照（核心功能）
```bash
agent-browser snapshot -i  # 只返回可交互元素（推荐）
```

**输出示例**：
```
- link "新闻" [ref=e1]
- textbox "搜索" [ref=e2]
- button "提交" [ref=e3]
```

### 3. 交互操作
```bash
agent-browser fill @e2 "红太阳数控切割机"  # 填充输入框
agent-browser click @e3                    # 点击按钮
agent-browser screenshot result.png        # 截图
```

### 4. 关闭浏览器
```bash
agent-browser close
```

## 常用命令

### 导航
```bash
agent-browser open <url>          # 打开网页
agent-browser close               # 关闭浏览器
```

### 快照与信息获取
```bash
agent-browser snapshot -i         # 获取可交互元素（推荐）
agent-browser snapshot -i -C      # 包含 cursor:pointer 的 div
agent-browser snapshot -s "#id"   # 限定范围（提升性能）

agent-browser get text @e1        # 获取文本
agent-browser get value @e1       # 获取输入框值
agent-browser get title           # 获取页面标题
agent-browser get url             # 获取当前 URL
```

### 交互操作
```bash
agent-browser click @e1           # 点击
agent-browser click @e1 --new-tab # 新标签页打开
agent-browser fill @e2 "text"     # 清空并填充
agent-browser type @e2 "text"     # 追加输入
agent-browser press Enter         # 按键
agent-browser hover @e1           # 悬停
agent-browser check @e1           # 勾选复选框
agent-browser select @e1 "value"  # 选择下拉选项
```

### 截图与导出
```bash
agent-browser screenshot page.png         # 截图
agent-browser screenshot --full           # 全页截图
agent-browser screenshot --annotate       # 带标注的截图
agent-browser pdf output.pdf              # 导出 PDF
```

### 语义查找
```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "test@test.com"
agent-browser find placeholder "Search" type "query"
```

### 高级操作
```bash
agent-browser eval "document.title"              # 执行 JS
agent-browser scroll down 500                    # 滚动
agent-browser scrollintoview @e1                 # 滚动到元素
```

## 使用场景

### 1. X/Twitter 监控（持久化登录）
```bash
# 使用 Kernel 云浏览器（持久化登录）
export KERNEL_API_KEY="your-api-key"
export KERNEL_PROFILE_NAME="twitter-monitor"
agent-browser -p kernel open https://x.com
agent-browser snapshot -i
agent-browser find text "红太阳" click
```

### 2. 竞品信息抓取
```bash
agent-browser open https://www.made-in-china.com
agent-browser snapshot -i
agent-browser find placeholder "Search" fill "CNC cutting machine"
agent-browser find role button click --name "Search"
agent-browser screenshot competitors.png
```

### 3. 客户调研（Reddit/YouTube）
```bash
agent-browser open https://www.reddit.com/r/CNC
agent-browser snapshot -i
agent-browser find text "leather cutting" click
agent-browser get text @e1  # 提取评论内容
```

## 云端浏览器（可选）

### Browser Use Cloud
```bash
export BROWSER_USE_API_KEY="your-api-key"
export AGENT_BROWSER_PROVIDER=browseruse
agent-browser open https://example.com
```

### Kernel（推荐用于持久化登录）
```bash
export KERNEL_API_KEY="your-api-key"
export KERNEL_PROFILE_NAME="my-profile"  # 自动保存登录状态
export KERNEL_STEALTH=true               # 绕过反爬虫
agent-browser -p kernel open https://example.com
```

**Kernel 配置**：
- `KERNEL_HEADLESS`：无头模式（`true`/`false`，默认 `false`）
- `KERNEL_STEALTH`：隐身模式（`true`/`false`，默认 `true`）
- `KERNEL_TIMEOUT_SECONDS`：会话超时（默认 300 秒）
- `KERNEL_PROFILE_NAME`：配置文件名（持久化 cookies/登录）

## 性能对比

| 操作 | agent-browser | 传统方式 | 节省比例 |
|------|---------------|----------|----------|
| 百度首页快照 | ~200 tokens | ~8,000 tokens | 97.5% |
| 搜索结果页快照 | ~1,200 tokens | ~50,000 tokens | 97.6% |
| 快照生成速度 | <0.5 秒 | ~1 秒 | 快 50% |

## 注意事项

1. **SSL 证书问题**：如果遇到 `ERR_CERT_DATE_INVALID`，检查目标网站的 SSL 证书是否有效
2. **元素数量限制**：复杂页面可能有数百个可交互元素，使用 `-s "#selector"` 限定范围
3. **无可视化界面**：默认无头模式，调试时可使用 `--headed` 参数（但会降低性能）
4. **云端浏览器成本**：Browser Use Cloud 和 Kernel 需要付费，评估 ROI 后再使用

## 故障排查

### 问题 1：命令未找到
```bash
# 检查是否全局安装
npm list -g agent-browser

# 重新安装
npm install -g agent-browser
```

### 问题 2：Chromium 未安装
```bash
agent-browser install
```

### 问题 3：网页无法打开
```bash
# 检查网络连接
curl -I <url>

# 检查 SSL 证书
openssl s_client -connect <domain>:443
```

## 最佳实践

1. **优先使用 snapshot -i**：只返回可交互元素，Token 消耗最低
2. **限定快照范围**：使用 `-s "#selector"` 提升性能
3. **持久化登录**：使用 Kernel 云浏览器，避免反复验证码
4. **错误处理**：检查命令返回状态，失败时重试或降级

## 参考资料

- GitHub 仓库：https://github.com/vercel-labs/agent-browser
- 官方文档：https://github.com/vercel-labs/agent-browser/blob/main/README.md
- Kernel 云浏览器：https://www.kernel.sh
- Browser Use Cloud：https://cloud.browser-use.com

## 更新记录

- **2026-03-03**：初始版本，agent-browser 0.15.2
- 安装测试通过，核心功能验证完成
- Token 节省效果：95%+（实测百度首页 200 tokens vs 8,000 tokens）
