# 2026-02-26 NotebookLM & Gemini 一条龙内容生产调研

**做了什么：**
对 NotebookLM 和 Gemini 的播客及 PPT 生成能力进行了 2025-2026 年最新进展的调研，并设计了自动化工作流。

**关键发现：**
1. **NotebookLM Audio Overview**：已支持中文等 50+ 语言，增加了时长和语气定制。官方有企业级 Podcast API（基于 GCP），民间有成熟的基于 Playwright 的 RPA 方案（如 `notebooklm-podcast-automator`）。
2. **NotebookLM Slides**：最新更新支持将文档直接转化为幻灯片，可通过 Prompt 修改，并支持 PPTX 格式下载导出。
3. **Gemini API**：已上线 Gemini 2.5 Native Audio，支持多说话人 TTS 合成。

**结果与结论：**
自动化链路**完全可行**。
- **低成本快捷路线**：利用 Playwright 脚本模拟点击 NotebookLM Web 端，自动获取生成的音频和 PPTX 文件，可轻易封装进 OpenClaw。
- **高稳定 API 路线**：使用 Gemini API 生成剧本 + Google Cloud TTS / ElevenLabs 生成多声轨音频；使用 Python `pptx` 或 Google Slides API 基于 Gemini 总结生成演示文稿。