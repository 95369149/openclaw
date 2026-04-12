# 2026-02-18 App Store Connect CLI: Agent 友好的发布工具 (@tualatrix)

## 来源

- Author: @tualatrix (图拉鼎)
- Date: 2026-02-17
- Link: https://x.com/tualatrix/status/2023667569522000253
- GitHub: https://github.com/rudrankriyam/App-Store-Connect-CLI

## 核心推荐

在 Agent 时代，推荐使用 **App-Store-Connect-CLI** 替代传统的 `fastlane`。

### 为什么适合 Agent?

- **CLI 原生**：基于 Swift 编写，提供纯净的命令行接口，方便 Agent 直接调用 (Exec Tool)。
- **结构清晰**：相比 fastlane 复杂的 Ruby DSL，这种 CLI 更符合 Unix 哲学，更易被 LLM 理解和组合。

### 功能

- 管理 TestFlight 测试员
- 更新 App Store 元数据 (Metadata)
- 上传截图
- 获取 App 状态

## Kitt 思考

- **工具链进化**：Agent-Ready 的工具往往具备简单的 CLI 接口、清晰的 JSON 输出。以后选择工具链时，优先考虑这种“Agent 友好型”替代品。
- **未来场景**：如果有 iOS 独立开发需求，直接让 Agent 调这个 CLI 就能完成全套上架流程。

<!-- digested: 2026-02-21 -->
