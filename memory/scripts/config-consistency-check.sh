#!/bin/bash
# 配置-文档一致性校验 v1.1
# 用途：检查 openclaw.json 实际配置与排兵布阵.md 文档是否一致
# 调用：bash config-consistency-check.sh
# 返回码：0=一致，1=不一致

set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
DOC="$HOME/.openclaw/workspace/memory/01_强制规则/排兵布阵.md"
ISSUES=0

echo "=== 配置-文档一致性校验 ==="
echo ""

if [ ! -f "$CONFIG" ]; then
  echo "❌ 配置文件不存在: $CONFIG"
  exit 1
fi

if [ ! -f "$DOC" ]; then
  echo "❌ 排兵布阵.md 不存在: $DOC"
  exit 1
fi

# 1) 提取实际配置的 agent -> model(primary)
echo "📋 实际配置（openclaw.json）："
ACTUAL=$(python3 - <<'PY'
import json
from pathlib import Path
cfg = Path.home() / '.openclaw' / 'openclaw.json'
with cfg.open() as f:
    c = json.load(f)
for a in c.get('agents', {}).get('list', []):
    aid = a.get('id', '?')
    m = a.get('model', '?')
    if isinstance(m, dict):
      m = m.get('primary') or '?'
    print(f"{aid}|{m}")
PY
)

while IFS='|' read -r id model; do
  [ -z "${id:-}" ] && continue
  printf "  %-8s → %s\n" "$id" "$model"
done <<< "$ACTUAL"

echo ""

# 2) 校验模型是否在文档中出现（固定字符串匹配，避免 grep 正则误伤）
echo "🔍 校验文档一致性："
while IFS='|' read -r id model; do
  [ -z "${id:-}" ] && continue
  if grep -Fq -- "$model" "$DOC"; then
    printf "  ✅ %-8s %s 在文档中\n" "$id" "$model"
  else
    printf "  ❌ %-8s %s 不在文档中！\n" "$id" "$model"
    ISSUES=$((ISSUES + 1))
  fi
done <<< "$ACTUAL"

# 3) 检查文档中是否有废弃项引用
echo ""
echo "🔍 检查废弃引用："
DEPRECATED=("siliconflow" "ai.ltcraft.cn" "DeepSeek-V3.2" "DeepSeek-R1" "llama-3.3-70b")
for dep in "${DEPRECATED[@]}"; do
  if grep -Fqi -- "$dep" "$DOC"; then
    echo "  ⚠️  文档仍引用废弃项: $dep"
    ISSUES=$((ISSUES + 1))
  fi
done

# 4) 打印 Fallback 链
echo ""
echo "🔍 校验 Fallback 链："
python3 - <<'PY'
import json
from pathlib import Path
cfg = Path.home() / '.openclaw' / 'openclaw.json'
with cfg.open() as f:
    c = json.load(f)
model = c.get('agents', {}).get('defaults', {}).get('model', {})
if isinstance(model, str):
    print(f"  primary: {model}")
else:
    print(f"  primary: {model.get('primary', '?')}")
    for i, fb in enumerate(model.get('fallbacks', [])):
        print(f"  fallback[{i}]: {fb}")
PY

# 5) 打印 provider 列表（当前结构是 models.providers）
echo ""
echo "🔍 Provider 列表："
python3 - <<'PY'
import json
from pathlib import Path
cfg = Path.home() / '.openclaw' / 'openclaw.json'
with cfg.open() as f:
    c = json.load(f)
providers = c.get('models', {}).get('providers', {})
for pid in providers.keys():
    print(f"  ✅ {pid}")
PY

echo ""
if [ "$ISSUES" -gt 0 ]; then
  echo "⚠️  发现 $ISSUES 个不一致项，请修复！"
  exit 1
else
  echo "✅ 配置与文档一致"
  exit 0
fi
