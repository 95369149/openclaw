#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

SAFE_TARGETS = [
    {
        "key": "browser-cache",
        "path": Path.home() / ".openclaw/browser/openclaw",
        "type": "dir",
        "reason": "OpenClaw 内置浏览器缓存，可重建",
        "default": True,
    },
    {
        "key": "workspace-kitt-projects",
        "path": Path.home() / ".openclaw/workspace-kitt/projects",
        "type": "dir",
        "reason": "Kitt 历史项目临时产物",
        "default": True,
    },
    {
        "key": "workspace-kitt-tmp",
        "path": Path.home() / ".openclaw/workspace-kitt",
        "type": "glob",
        "pattern": "tmp*",
        "reason": "Kitt 临时目录",
        "default": True,
    },
    {
        "key": "logs-old",
        "path": Path.home() / ".openclaw/logs",
        "type": "aged-files",
        "days": 14,
        "reason": "14 天前日志",
        "default": True,
    },
    {
        "key": "media-old",
        "path": Path.home() / ".openclaw/media",
        "type": "aged-files",
        "days": 14,
        "reason": "14 天前媒体缓存",
        "default": False,
    },
    {
        "key": "workspace-node-modules",
        "path": Path.home() / ".openclaw/workspace/node_modules",
        "type": "dir",
        "reason": "workspace 依赖目录，可按需重装",
        "default": False,
    },
    {
        "key": "mediacrawler",
        "path": Path.home() / ".openclaw/workspace/MediaCrawler",
        "type": "dir",
        "reason": "历史项目目录，删除前需确认不再使用",
        "default": False,
    },
]

NEVER_DELETE_PREFIXES = [
    str(Path.home() / ".openclaw/credentials"),
    str(Path.home() / ".openclaw/openclaw.json"),
    str(Path.home() / ".openclaw/.env"),
    str(Path.home() / ".openclaw/workspace/memory"),
    str(Path.home() / ".openclaw/agents"),
    str(Path.home() / ".openclaw/cron"),
]


def is_protected(path: Path) -> bool:
    rp = str(path.resolve()) if path.exists() else str(path)
    return any(rp == p or rp.startswith(p + os.sep) for p in NEVER_DELETE_PREFIXES)


def size_of(path: Path) -> int:
    try:
        if path.is_symlink() or path.is_file():
            return path.stat().st_size
        total = 0
        for root, _, files in os.walk(path):
            for name in files:
                fp = Path(root) / name
                try:
                    if not fp.is_symlink():
                        total += fp.stat().st_size
                except FileNotFoundError:
                    pass
        return total
    except FileNotFoundError:
        return 0


def fmt_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.1f}{u}"
        x /= 1024
    return f"{n}B"


def list_aged_files(base: Path, days: int):
    cutoff = time.time() - days * 86400
    out = []
    if not base.exists():
        return out
    for p in base.rglob("*"):
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                out.append(p)
        except FileNotFoundError:
            pass
    return out


def collect(selected_keys):
    items = []
    for target in SAFE_TARGETS:
        if selected_keys and target["key"] not in selected_keys:
            continue
        t = target["type"]
        base = target["path"]
        if t == "dir":
            if base.exists() and not is_protected(base):
                items.append((target, base, size_of(base)))
        elif t == "glob":
            for p in sorted(base.glob(target["pattern"])):
                if p.exists() and not is_protected(p):
                    items.append((target, p, size_of(p)))
        elif t == "aged-files":
            for p in list_aged_files(base, target["days"]):
                if p.exists() and not is_protected(p):
                    items.append((target, p, size_of(p)))
    return items


def delete_path(path: Path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Safe OpenClaw cleanup")
    parser.add_argument("--apply", action="store_true", help="Actually delete files")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--include", action="append", default=[], help="Cleanup key to include; repeatable")
    parser.add_argument("--defaults", action="store_true", help="Use only default-safe targets")
    args = parser.parse_args()

    selected = set(args.include)
    if args.defaults and not selected:
        selected = {t["key"] for t in SAFE_TARGETS if t.get("default")}

    items = collect(selected)
    total = sum(size for _, _, size in items)
    result = {
        "mode": "apply" if args.apply else "dry-run",
        "count": len(items),
        "totalBytes": total,
        "totalHuman": fmt_bytes(total),
        "items": [
            {
                "key": target["key"],
                "path": str(path),
                "sizeBytes": size,
                "sizeHuman": fmt_bytes(size),
                "reason": target["reason"],
            }
            for target, path, size in items
        ],
    }

    if args.apply:
        deleted = []
        for _, path, _ in items:
            try:
                delete_path(path)
                deleted.append(str(path))
            except Exception as e:
                deleted.append(f"ERROR:{path}:{e}")
        result["deleted"] = deleted

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Items: {result['count']}")
        print(f"Reclaimable: {result['totalHuman']}")
        for item in result["items"]:
            print(f"- [{item['key']}] {item['sizeHuman']}  {item['path']}  # {item['reason']}")
        if args.apply:
            print("Deleted:")
            for x in result["deleted"]:
                print(f"  - {x}")

if __name__ == "__main__":
    sys.exit(main())
