# NotebookLM 工作流

> 最后更新：2026-03-11

## 核心规则

### 上传前必须清理
- 每次上传新版本前，先删除旧版本/重复 source
- 用 `notebooklm` CLI 的 delete-source 命令
- 不清理会导致 NotebookLM 混淆新旧内容

### Source 管理
- 每个 notebook 保持 source 数量最少
- 同一份教材只保留最新版本
- 图片 source 可以保留多个（不会冲突）

### PPT/Artifact 生成
- 生成后用 download-artifact 下载到桌面
- 语言设置：zh_Hans
- 生成可能需要几分钟，耐心等待

## 常见错误

### 1. Source 重复
- 症状：生成内容混合新旧版本
- 修复：删除所有旧 source，只保留最新

### 2. 上传失败
- 症状：add-source 返回错误
- 修复：检查文件大小（<50MB），检查格式（支持 md/txt/pdf）

### 3. Artifact 下载失败
- 症状：download-artifact 报错
- 修复：确认 artifact ID 正确，确认生成已完成

## Notebook 清单
- 钳工电工培训教材PPT：f97d30f0-6b17-4ba6-9b25-751b13503a3c
- 钳工岗位培训教材：68a5a64b-3afc-41e1-8177-811d7ccd925e
- 电工岗位培训教材：0b9ef92f-6bc0-43b2-a448-5e73af1a4d71
