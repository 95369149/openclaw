# iCloud 同步防套娃规则 v2.0

## 问题根源
1. **双向同步**：iCloud会把删除的文件重新推回来
2. **rsync冲突**：本地→云端同步时，云端旧文件未清理干净
3. **launchd触发频繁**：文件变化触发同步，同步又触发变化，死循环

## 解决方案

### 1. 同步策略：单向覆盖
```bash
# sync-cloud.sh v4.0 核心逻辑
# 先清空目标，再写入源
rm -rf "$CLOUD/黄金备份/latest"
rsync -a --delete --exclude-from=.rsync-exclude \
  "$WORKSPACE/memory/" "$CLOUD/黄金备份/latest/memory/"
```

### 2. 排除规则：.rsync-exclude
```
# 永远不同步到云端的目录
黄金备份
agents
engine_data
short_term
long_term
inbox
working
_meta
建议提案箱
03_semantic-memory
03_知识库
03_%E8%AF%AD%E4%B9%89%E8%AE%B0%E5%BF%86
*.log
*.tmp
.DS_Store
```

### 3. launchd 触发：定时而非监控
```xml
<!-- 旧方案（会死循环）-->
<key>WatchPaths</key>
<array>
  <string>/Users/apple/.openclaw/workspace/memory</string>
</array>

<!-- 新方案（30分钟定时）-->
<key>StartInterval</key>
<integer>1800</integer>
```

### 4. 清理脚本：定期执行
```bash
# 每天凌晨3点清理iCloud套娃
0 3 * * * /Users/apple/.openclaw/workspace/memory/scripts/icloud-cleanup-v2.sh
```

### 5. 目录结构约定
**iCloud只存两个目录：**
- `黄金备份/` — kitt的备份（latest/weekly/monthly）
- `agents/` — 其他agent的独立备份

**本地workspace结构：**
```
memory/
├── 01_强制规则/
├── 02_知识库/
├── 03_语义记忆/
├── 04_情景记忆/
├── 05_日常日志/
├── 07_版本控制/
├── 10_项目/
├── 20_领域/
├── 80_收藏/
├── 90_归档/
└── scripts/
    ├── engine_data/  (不同步)
    └── sync-cloud.sh
```

## 检查清单
- [ ] `.rsync-exclude` 已部署到所有agent workspace
- [ ] `sync-cloud.sh` 使用 `rm -rf` + `rsync -a --delete`
- [ ] launchd 改为 `StartInterval` 定时触发
- [ ] iCloud根目录只有 `agents/` 和 `黄金备份/`
- [ ] 定期运行 `icloud-cleanup-v2.sh` 清理套娃

## 应急处理
如果再次出现套娃：
```bash
# 1. 立即清理
bash /Users/apple/.openclaw/workspace/memory/scripts/icloud-cleanup-v2.sh

# 2. 停止launchd
launchctl unload ~/Library/LaunchAgents/ai.openclaw.cloud-sync.plist

# 3. 手动同步一次
bash /Users/apple/.openclaw/workspace/memory/scripts/sync-cloud.sh

# 4. 重新启动launchd
launchctl load ~/Library/LaunchAgents/ai.openclaw.cloud-sync.plist
```

---
**更新时间**: 2026-02-25  
**版本**: v2.0  
**维护者**: kitt
