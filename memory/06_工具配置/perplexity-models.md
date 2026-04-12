# Perplexity 模型配置

> 模型选择是全局的，每次调用前需切换到目标模型。

## 可用模型

| 模型 | 用途 | 备注 |
|------|------|------|
| **Sonar** | 快速搜索、事实查证 | Perplexity 自家模型 |
| **GPT-5.2** | 深度推理、复杂方案设计 | |
| **Claude Sonnet 4.6** | 架构设计、代码审查 | |
| **Grok 4.1** | 反向验证、独立视角 | |
| **Kimi K2.5** | 中文内容、国内市场分析 | 托管在美国 |
| **Gemini 3 Flash** | 快速分析、低成本 | |
| **Gemini 3.1 Pro** | 多模态、长文档 | |

## 不可用

- **Claude Opus 4.6 Max** — 需升级会员

## 调用流程

1. `browser open https://www.perplexity.ai`
2. 点模型按钮（输入框右侧）→ 展开菜单 → 选目标模型
3. 在输入框输入问题并提交
4. 等待回复 → evaluate 提取 prose 内容

---

**最后更新**: 2026-02-25

---

# Whisper 语音转文字

**已安装**: openai-whisper 20240930
**调用方式**: `python3 -m whisper <音频文件> --language zh --model tiny --output_format txt --output_dir /tmp/`
**支持格式**: ogg, mp3, wav, m4a 等
**注意**: tiny 模型速度快但准确率一般，重要语音可用 small 或 base 模型
