#!/usr/bin/env python3
"""
bootstrap.py - 记忆强制读取机制
每次新 session / 模型切换 / 压缩恢复后，强制先读记忆再允许 LLM 调用

用法:
  from runtime.bootstrap import BootstrapManager
  bm = BootstrapManager()
  bm.ensure_bootstrapped(session_id, model_id, llm_context)
"""
from pathlib import Path
from typing import Optional
import json
import time

WORKSPACE = Path("/Users/apple/.openclaw/workspace")
SESSION_DIR = WORKSPACE / "state/sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

BOOTSTRAP_TTL = 7200  # 2小时内同模型不重复读


class BootstrapManager:
    def __init__(self, ttl_seconds=BOOTSTRAP_TTL):
        self.ttl = ttl_seconds

    def _state_file(self, session_id: str) -> Path:
        return SESSION_DIR / f"{session_id}.json"

    def load_state(self, session_id: str) -> Optional[dict]:
        f = self._state_file(session_id)
        if not f.exists():
            return None
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return None

    def save_state(self, session_id: str, state: dict):
        self._state_file(session_id).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def is_bootstrapped(self, session_id: str, model_id: str) -> bool:
        state = self.load_state(session_id)
        if not state:
            return False
        if state.get("last_model_id") != model_id:
            return False
        if time.time() - state.get("last_bootstrap_at", 0) > self.ttl:
            return False
        return True

    def ensure_bootstrapped(self, session_id: str, model_id: str, llm_context=None) -> dict:
        if self.is_bootstrapped(session_id, model_id):
            return self.load_state(session_id)

        abstract = self._read_file(WORKSPACE / "memory/.abstract", max_chars=1500)
        task_board = self._read_file(WORKSPACE / "memory/task-board.json", max_chars=1500)
        shared_index = self._read_shared_index()

        summary = (
            "=== MEMORY_BOOTSTRAP ===\n"
            f"[.abstract]\n{abstract}\n\n"
            f"[task-board]\n{task_board}\n\n"
            f"[shared_index]\n{shared_index}\n"
            "========================\n"
        )

        state = {
            "session_id": session_id,
            "last_model_id": model_id,
            "last_bootstrap_at": time.time(),
            "bootstrap_sources": ["memory/.abstract", "memory/task-board.json", "memory/shared/index.json"],
            "digest": summary[:4000],
        }
        self.save_state(session_id, state)

        if llm_context and hasattr(llm_context, "inject_system"):
            llm_context.inject_system(summary)

        return state

    def _read_file(self, path: Path, max_chars=2000) -> str:
        if not path.exists():
            return f"[{path.name} not found]"
        try:
            return path.read_text(encoding="utf-8")[:max_chars]
        except Exception as e:
            return f"[read error: {e}]"

    def _read_shared_index(self) -> str:
        index_path = WORKSPACE / "memory/shared/index.json"
        if index_path.exists():
            return self._read_file(index_path, max_chars=1000)
        # 没有 index 就列最近 5 个 shared 文件
        shared_dir = WORKSPACE / "memory/shared"
        if not shared_dir.exists():
            return "[]"
        files = sorted(shared_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
        return json.dumps([f.name for f in files], ensure_ascii=False)


if __name__ == "__main__":
    import sys
    session_id = sys.argv[1] if len(sys.argv) > 1 else "test-session"
    model_id = sys.argv[2] if len(sys.argv) > 2 else "claude-sonnet"

    bm = BootstrapManager()
    state = bm.ensure_bootstrapped(session_id, model_id)
    print(json.dumps(state, ensure_ascii=False, indent=2))
