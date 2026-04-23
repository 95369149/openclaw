# Google 生态内容生产链路调研：NotebookLM + Gemini

## 1. NotebookLM 播客功能 (Audio Overview)
- **功能现状**：NotebookLM 提供 Audio Overview 功能，能将上传的文档转化为播客形式的音频对话。2025年3月更新后，支持更精细的控制（语气、时长、重点突出）。
- **语言支持**：2025年4月开始，Audio Overview 扩展支持 50 多种语言，包括中文。
- **API 调用**：
  - **官方企业级 API**：通过 Google Cloud 的 NotebookLM Enterprise 提供 Podcast API（依赖 Discovery Engine API）。
  - **民间非官方方案**：例如 GitHub 上的 `israelbls/notebooklm-podcast-automator`，利用 FastAPI + Playwright 浏览器自动化来绕过无公开 API 的限制，实现程序化上传文档并生成播客音频。

## 2. NotebookLM PPT/演示文稿功能
- **功能现状**：NotebookLM 在2025-2026年的更新中加入了将文档转化为幻灯片 (Slide Deck) 的功能。
- **编辑与导出**：支持通过文本提示词 (Prompt) 进行幻灯片的迭代修改，并且支持直接导出为 **PPTX 格式**或 PDF，方便在 Google Slides 或 Microsoft PowerPoint 中二次编辑。
- **自动化情况**：目前主要依托 Web 界面进行生成和编辑，官方暂未提供直接生成 PPT 的轻量级独立 API。

## 3. Gemini App / API 内容生成通道
- **Gemini App**：App 端支持直接交互生成内容，但复杂的多角色播客合成体验不如 NotebookLM 专注。
- **Gemini API**：
  - Gemini API 提供了强大的 **Text-to-speech (TTS)** 功能，支持单说话人或多说话人音频生成。
  - 2025年底/2026年，**Gemini 2.5 Native Audio**（原生音频模型）已在 Vertex AI 和 Gemini API 预览版中可用，可以直接生成高质量音频回复。

## 4. 自动化方案设计 (一条龙工作流)

**工作流路径**：文字/文档 → 音频 + PPT → 下载分发

**方案 A：基于企业级 API (推荐用于规模化)**
- **步骤**：使用 Google Cloud NotebookLM Enterprise 的 Podcast API，上传文档生成音频。PPT 生成若无直接 API，可结合 Gemini API 将内容提取为大纲，再借助 Google Slides API 自动生成排版。

**方案 B：基于 Playwright 的 RPA 方案 (成本低，适合轻量级)**
1. **文档上传与音频生成**：使用基于 Playwright 的脚本（如 `notebooklm-podcast-automator`）自动登录 NotebookLM Web 端，上传文档并触发 Audio Overview 生成，等待完成后爬取音频下载链接。
2. **PPT 导出**：在同一个 Playwright 会话中，触发 "Generate a Slide Deck"，并点击下载 PPTX 按钮保存至本地。
3. **OpenClaw 集成**：可以将上述 Playwright 脚本封装为 OpenClaw 的一个 Skill 或通过 `exec` 定时执行。

## 5. 替代方案与成本对比
如果 NotebookLM 自动化成本高或不稳定，可使用：
- **方案**：Gemini API (生成双人对话脚本) + Google Cloud TTS (或 ElevenLabs) (语音合成)。
- **操作**：先让 Gemini 读取文档并输出带角色的对话脚本。然后调用多音色 TTS 接口合成最终音频。
- **成本对比**：
  - **NotebookLM Playwright**：极低（仅服务器资源），但稳定性较差（页面改版即失效）。
  - **Google Cloud TTS + Gemini API**：按字符/Token计费，成本可控，开发灵活，稳定性极高。
  - **ElevenLabs**：语音极其逼真，但成本相对较高。

## 结论
**能打通。**
- 如果追求**最接近 NotebookLM 官方播客的听感**，建议采用 **Playwright 浏览器自动化方案**（封装进 OpenClaw）。
- 如果追求**高稳定性的纯 API 工作流**，建议采用 **Gemini 脚本生成 + 云端 TTS（多音色）合成** 作为替代路线；PPT 侧用 Gemini 提炼后调用 Google Slides API 或 Python-pptx 库生成。