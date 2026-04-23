#!/usr/bin/env python3
"""
fs_guard.py - 项目保护 & 文件操作守门器
所有删除/归档操作必须经过此模块，禁止直接 os.remove / shutil.rmtree

用法:
  from runtime.fs_guard import FileGuard, ProtectedProjectError
  guard = FileGuard()
  guard.delete("/path/to/file", reason="清理")
  guard.archive("/path/to/file", reason="归档", archive_class="patrol")
"""
from pathlib import Path
import json
import shutil
import yaml

WORKSPACE = Path("/Users/apple/.openclaw/workspace")
PROTECTION_CONFIG = WORKSPACE / "config/project_protection.yml"
TASK_BOARD = WORKSPACE / "memory/task-board.json"


class ProtectedProjectError(Exception):
    pass


class FileGuard:
    def __init__(self):
        self.protection = self._load_protection()

    def _load_protection(self) -> dict:
        if PROTECTION_CONFIG.exists():
            try:
                return yaml.safe_load(PROTECTION_CONFIG.read_text(encoding="utf-8")) or {}
            except Exception:
                pass
        return {}

    def _load_task_board_paths(self) -> list[str]:
        if not TASK_BOARD.exists():
            return []
        try:
            board = json.loads(TASK_BOARD.read_text(encoding="utf-8"))
            paths = []
            for proj in board.get("projects", []):
                paths.extend(proj.get("workspace_paths", []))
            return paths
        except Exception:
            return []

    def is_protected(self, path: str) -> bool:
        p = Path(path).as_posix()

        # 全局保护路径
        for gp in self.protection.get("global_protected_paths", []):
            if p.startswith(gp.rstrip("/")) or gp.rstrip("/") in p:
                return True

        # 项目保护路径
        for proj in self.protection.get("projects", []):
            for prefix in proj.get("paths", []):
                if p.startswith(prefix.rstrip("/")) or prefix.rstrip("/") in p:
                    return True
            # 别名匹配
            for alias in proj.get("aliases", []):
                if alias in p:
                    return True

        # task-board 里的项目路径
        for tb_path in self._load_task_board_paths():
            if p.startswith(tb_path.rstrip("/")) or tb_path.rstrip("/") in p:
                return True

        return False

    def delete(self, path: str, reason: str = "", task_meta=None):
        if self.is_protected(path):
            raise ProtectedProjectError(
                f"DELETE blocked: '{path}' is a protected project path.\n"
                f"Allowed: archive/index only. Reason attempted: {reason}"
            )
        p = Path(path)
        if not p.exists():
            return
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink(missing_ok=True)

    def archive(self, path: str, reason: str = "", archive_class: str = "general", task_meta=None):
        p = Path(path)
        if not p.exists():
            return

        # 项目文件只能归档到项目归档区，不能删
        if self.is_protected(path):
            archive_root = WORKSPACE / "archive/projects"
        else:
            archive_root = WORKSPACE / f"archive/{archive_class}"

        archive_root.mkdir(parents=True, exist_ok=True)
        dest = archive_root / p.name

        # 避免覆盖
        if dest.exists():
            dest = archive_root / f"{p.stem}_{int(Path(path).stat().st_mtime)}{p.suffix}"

        shutil.move(str(p), str(dest))
        return str(dest)

    def safe_check(self, path: str) -> dict:
        """检查路径是否受保护，返回状态"""
        protected = self.is_protected(path)
        return {
            "path": path,
            "protected": protected,
            "allowed_ops": ["read", "archive", "index"] if protected else ["read", "archive", "delete", "index"],
        }


if __name__ == "__main__":
    import sys
    guard = FileGuard()
    path = sys.argv[1] if len(sys.argv) > 1 else "memory/10_项目/test"
    result = guard.safe_check(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
