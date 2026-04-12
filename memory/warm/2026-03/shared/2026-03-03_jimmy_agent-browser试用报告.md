# agent-browser 试用报告
> 试用时间：2026-03-03 14:32-14:35
> 试用者：jimmy
> 场景：X/Twitter 登录页面测试

## 试用过程

### 1. 打开 X 首页
```bash
agent-browser open https://x.com
```
- 结果：✅ 成功
- 耗时：~3 秒

### 2. 获取首页快照
```bash
agent-browser snapshot -i | head -50
```
- 结果：✅ 成功
- 输出：31 个可交互元素
- **关键发现**：
  - Cookie 同意按钮（`@e1`、`@e2`、`@e3`）
  - 注册按钮（Google/Apple 登录）
  - **登录链接**（`@e10`）
  - 页脚链接（帮助中心、隐私政策等）

**示例输出**：
```
- button "Accept all cookies" [ref=e2]
- button "Sign up with Google" [ref=e4]
- link "Sign in" [ref=e10]
- link "Get Grok" [ref=e11]
```

### 3. 点击登录链接
```bash
agent-browser click @e10
```
- 结果：✅ 成功
- 输出：`✓ Done`
- **验证**：页面跳转到登录页

### 4. 获取登录页快照
```bash
agent-browser snapshot -i | head -30
```
- 结果：✅ 成功
- 输出：4 个可交互元素
- **关键发现**：
  - Cookie 同意按钮（`@e1`、`@e2`、`@e3`）
  - **Retry 按钮**（`@e4`）
  - **没有登录表单**（可能需要等待加载或被反爬虫拦截）

**示例输出**：
```
- button "Accept all cookies" [ref=e2]
- button "Retry" [ref=e4]
```

### 5. 截图验证
```bash
agent-browser screenshot /tmp/x-login-page.png
```
- 结果：✅ 成功
- 截图已保存到 `/tmp/x-login-page.png`

### 6. 关闭浏览器
```bash
agent-browser close
```
- 结果：✅ 成功

---

## 关键发现

### 1. X/Twitter 有反爬虫机制
- 点击登录后，页面只显示 "Retry" 按钮
- 没有出现登录表单（用户名/密码输入框）
- **可能原因**：
  - X 检测到无头浏览器（Chromium）
  - 需要 JavaScript 完全加载后才显示表单
  - 需要通过 Cookie 或 User-Agent 验证

### 2. 需要云端浏览器（Kernel）
- 本地无头浏览器容易被 X 识别
- **解决方案**：
  - 使用 Kernel 云浏览器（`KERNEL_STEALTH=true`）
  - 持久化登录（`KERNEL_PROFILE_NAME`）
  - 避免反复触发验证码

### 3. Token 优化效果依然显著
- X 首页：31 个元素 → ~200 tokens
- 登录页：4 个元素 → ~30 tokens
- 即使被反爬虫拦截，Token 消耗依然极低

---

## 下一步测试计划

### 1. 测试 Kernel 云浏览器（需要 API key）
```bash
export KERNEL_API_KEY="your-api-key"
export KERNEL_PROFILE_NAME="x-monitor"
export KERNEL_STEALTH=true
agent-browser -p kernel open https://x.com
```

### 2. 测试其他网站（无反爬虫）
- Made-in-China（竞品信息）
- Reddit（客户调研）
- YouTube（视频评论）

### 3. 集成到 X 监控脚本
- 替换现有的浏览器抓取逻辑
- 使用 Kernel 持久化登录
- 降低 Token 消耗

---

## 结论

✅ **agent-browser 基础功能验证通过**

**优势**：
1. Token 节省效果显著（31 个元素 ~200 tokens）
2. 速度快（快照生成 <0.5 秒）
3. 引用机制直观（`@e10` 直接点击）

**限制**：
1. X/Twitter 有反爬虫机制，本地无头浏览器容易被拦截
2. 需要云端浏览器（Kernel）绕过检测
3. 持久化登录需要付费（Kernel API key）

**建议**：
1. 申请 Kernel API key（评估成本）
2. 先在无反爬虫的网站测试（Made-in-China、Reddit）
3. 验证 Token 节省效果后，再决定是否付费使用 Kernel

**下一步**：
1. 测试 Made-in-China 竞品抓取
2. 评估 Kernel 云浏览器的 ROI
3. 更新 X 监控脚本（集成 agent-browser）
