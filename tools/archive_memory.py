#!/usr/bin/env python3
"""
archive_memory.py - 记忆归档清理
扫描 memory/shared/ 下过期文件，move 到 archive/，项目类路径不动

用法: python3 tools/archive_memory.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional
import yaml

BASE_DIR = Path("/Users/apple/.openclaw/workspace")
MEM_DIR = BASE_DIR / "memory"
ARCHIVE_DIR = BASE_DIR / "archive"
LOG_FILE = BASE_DIR / "logs/archive_memory.log"

LIFECYCLE_CONFIG = BASE_DIR / "config/memory_lifecycle.yml"

# 永远不归档的路径
NEVER_ARCHIVE = [
    "memory/task-board.json",
    "memory/.abstract",
    "memory/01_强制规则/",
    "memory/10_项目/",
    "SOUL.md",
    "IDENTITY.md",
    "AGENTS.md",
    "MEMORY.md",
]


def log(msg: str):
    t = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def is_protected(path: Path) -> bool:
    rel = str(path.relative_to(BASE_DIR))
    for p in NEVER_ARCHIVE:
        if rel.startswith(p.rstrip("/")):
            return True
    # 也读 project_protection.yml
    prot_cfg = BASE_DIR / "config/project_protection.yml"
    if prot_cfg.exists():
        try:
            data = yaml.safe_load(prot_cfg.read_text(encoding="utf-8")) or {}
            for gp in data.get("global_protected_paths", []):
                if rel.startswith(gp.rstrip("/")):
                    return True
            for proj in data.get("projects", []):
                for pp in proj.get("paths", []):
                    if rel.startswith(pp.rstrip("/")):
                        return True
        except Exception:
            pass
    return False


def load_lifecycle() -> dict:
    if not LIFECYCLE_CONFIG.exists():
        return {}
    try:
        return yaml.safe_load(LIFECYCLE_CONFIG.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def archive_files(src_dir: Path, archive_dir: Path, ttl_days: int, pattern: str = "*") -> int:
    if not src_dir.exists():
        return 0
    cutoff = time.time() - ttl_days * 86400
    n = 0
    for p in src_dir.rglob(pattern):
        if not p.is_file():
            continue
        if is_protected(p):
            continue
        if p.stat().st_mtime >= cutoff:
            continue
        rel = p.relative_to(src_dir)
        dest = archive_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest.parent / f"{p.stem}_{int(p.stat().st_mtime)}{p.suffix}"
        log(f"archive: {p} -> {dest}")
        p.rename(dest)
        n += 1
    return n


def main():
    conf = load_lifecycle()
    classes = conf.get("classes", {})
    total = 0

    for cls_name, cls_conf in classes.items():
        ttl = int(cls_conf.get("ttl_days", 30))
        path_prefix = cls_conf.get("path_prefix", "")
        pattern = cls_conf.get("filename_pattern", "*")
        archive_path = cls_conf.get("archive_path", f"archive/{cls_name}/")

        src = BASE_DIR / path_prefix.rstrip("/")
        dst = BASE_DIR / archive_path.rstrip("/")

        log(f"class={cls_name} ttl={ttl}d src={src}")
        n = archive_files(src, dst, ttl, pattern)
        log(f"class={cls_name} archived={n}")
        total += n

    log(f"archive_memory done: total={total} files archived")


if __name__ == "__main__":
    sys.path.insert(0, str(BASE_DIR))
    main()
