# 语义记忆：OpenClaw 运维模式

## gateway token mismatch 处理

当 gateway 重启后 config.patch 报 token mismatch：

- 不要反复调 API
- 直接用 python3 改 openclaw.json 文件
- 改完让厂长 `openclaw gateway restart`

## 配置修改标准流程

1. 能用 config.patch → 用 config.patch（自动重启）
2. config.patch 失败 → 直接改 JSON 文件 + 手动重启
3. 不要超过 2 次重试

## 权限受限操作

- /usr/local/lib 下的文件需要 sudo
- 没有 brew（未安装 Homebrew）
- 二进制工具放 ~/bin/
- npm 全局安装需要 sudo

## 已安装的工具

- gh CLI v2.86.0 → ~/bin/gh
- GitHub PAT → ~/.config/github-token
