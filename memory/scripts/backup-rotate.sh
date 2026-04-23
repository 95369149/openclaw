#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${1:-$HOME/.openclaw/workspace/memory/backup}"

if [ ! -d "$BACKUP_DIR" ]; then
  echo "backup dir not found: $BACKUP_DIR" >&2
  exit 1
fi

python3 - "$BACKUP_DIR" <<'PY'
import os, sys, time

backup_dir = sys.argv[1]
now = time.time()
entries = []
for name in os.listdir(backup_dir):
    path = os.path.join(backup_dir, name)
    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        age_days = (now - mtime) / 86400
        entries.append((name, mtime, age_days))

entries.sort(key=lambda item: item[1], reverse=True)
keep = []
used = set()

# 1. 最近变更前备份 1 份
if entries:
    keep.append(entries[0][0])
    used.add(entries[0][0])

# 2. 当天备份 1 份
for name, mtime, age_days in entries:
    if age_days <= 1 and name not in used:
        keep.append(name)
        used.add(name)
        break

# 3. 3 天内备份 1 份
for name, mtime, age_days in entries:
    if age_days <= 3 and name not in used:
        keep.append(name)
        used.add(name)
        break

# 4. 7 天内备份 1 份
for name, mtime, age_days in entries:
    if age_days <= 7 and name not in used:
        keep.append(name)
        used.add(name)
        break

remove = [name for name, _, _ in entries if name not in used]

print('KEEP:')
for name in keep:
    print(name)
print('---')
print('REMOVE:')
for name in remove:
    print(name)
    os.remove(os.path.join(backup_dir, name))
PY
