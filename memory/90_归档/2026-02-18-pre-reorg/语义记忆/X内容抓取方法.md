# 语义记忆：X 内容抓取方法

## 免费抓取方案（2026-02-16 验证可用）

### api.fxtwitter.com（推荐）

- 将 x.com 替换为 api.fxtwitter.com
- 返回完整 JSON：推文全文、作者信息、媒体链接、引用推文
- 免费、无需 API key、无速率限制（合理使用）
- 支持 Thread 串读

### vxtwitter.com

- 返回 HTML，适合嵌入预览
- 视频内容会重定向

### 不可用

- x.com 直接抓取：动态渲染，web_fetch 拿不到内容
- nitter.net：已失效

## 完整管线设计

1. 抓取：api.fxtwitter.com（推文）+ web_fetch（网页文章）
2. 路由：链接类型自动识别（x.com / reddit / 普通网页）
3. 分析：批判性分析 + 价值萃取
4. 输出：核心观点 + 逻辑硬伤 + 能学到什么 + 行动项
5. 记忆：存入 memory/收藏/
