# OpenClaw 社区 QA 精选

## 来源

- Site: https://ythx-101.github.io/openclaw-qa/
- Author: Community / @YuLin807

## Q: 本地 Git 能否实现自动部署 (CI/CD)?

**A: 可以！核心是 Git Hooks。**

### 方案 1: Git Hooks (推荐)

在 `.git/hooks/post-commit` 中编写脚本，每次 commit 后自动执行构建或备份。

```bash
#!/bin/bash
echo "🚀 自动备份触发..."
git push origin main
rsync -avz memory/ /backup/memory/
```

### 方案 2: Self-hosted CI

使用 Drone CI 或 Gitea Actions，兼容 GitHub Actions 语法但数据在本地。

### OpenClaw 实战案例

- 每小时自动 commit (保存进度)
- 每天 04:00 同步到 Obsidian (备份)
- 推送后自动部署网页

## 核心哲学

**能本地就本地，隐私 > 便利。**

## Kitt 思考

- **数据安全**：目前的 memory 系统缺乏版本控制和异地备份。应尽快引入 Git 管理 memory 目录，并配置 post-commit hook 自动同步。
- **工作流集成**：结合 Issue System，在 commit message 中关联 Issue ID (e.g. `git commit -m "feat: port revealjs skill (Fixes #001)"`)。
