"""
记忆管理器 v3.0 — Kitt 的海马体
适配 v3.0 目录结构，索引存 engine_data/
"""
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from config import *


class MemoryManager:
    def __init__(self):
        self.index = self._load_index()

    def _load_index(self) -> dict:
        if INDEX_FILE.exists():
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        return {"entries": {}, "tags": {}, "stats": {"total": 0, "last_gc": None}}

    def _save_index(self):
        INDEX_FILE.write_text(
            json.dumps(self.index, ensure_ascii=False, indent=2), encoding="utf-8")

    def _make_id(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def remember(self, content: str, tags: list = None,
                 priority: int = 5, source: str = "unknown",
                 target_dir: str = "03_语义记忆") -> str:
        tags = tags or []
        mem_id = self._make_id(content + str(time.time()))
        now = datetime.now().isoformat()

        dest = MEMORY_ROOT / target_dir
        dest.mkdir(parents=True, exist_ok=True)
        file_path = dest / f"{mem_id}.md"
        header = f"# {tags[0] if tags else 'memo'}\n> id: {mem_id} | priority: {priority} | source: {source}\n> tags: {', '.join(tags)}\n\n"
        file_path.write_text(header + content, encoding="utf-8")

        self.index["entries"][mem_id] = {
            "file": str(file_path.relative_to(MEMORY_ROOT)),
            "tags": tags, "priority": priority,
            "created_at": now, "summary": content[:100],
        }
        for tag in tags:
            self.index["tags"].setdefault(tag, []).append(mem_id)
        self.index["stats"]["total"] += 1
        self._save_index()
        return mem_id

    def recall(self, query: str = None, tags: list = None, top_k: int = 5) -> list:
        candidates = []
        for mem_id, meta in self.index["entries"].items():
            if tags and not set(tags) & set(meta["tags"]):
                continue
            if query and query.lower() not in meta["summary"].lower():
                if not any(query.lower() in t.lower() for t in meta["tags"]):
                    continue
            candidates.append(meta | {"id": mem_id})

        now = datetime.now()
        def score(entry):
            created = datetime.fromisoformat(entry["created_at"])
            age_hours = max((now - created).total_seconds() / 3600, 1)
            return entry["priority"] / (age_hours ** 0.3)

        candidates.sort(key=score, reverse=True)
        return candidates[:top_k]

    def reindex(self) -> dict:
        self.index = {"entries": {}, "tags": {}, "stats": {"total": 0, "last_gc": None}}
        count = 0
        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if any(str(rel).startswith(s) for s in ("90_归档", "scripts", "黄金备份")):
                continue
            content = md.read_text(encoding="utf-8", errors="ignore")[:200]
            mem_id = self._make_id(str(rel))
            self.index["entries"][mem_id] = {
                "file": str(rel),
                "tags": [rel.parts[0]] if len(rel.parts) > 1 else ["root"],
                "priority": 5,
                "created_at": datetime.fromtimestamp(md.stat().st_mtime).isoformat(),
                "summary": content.replace("\n", " ")[:100],
            }
            count += 1
        self.index["stats"]["total"] = count
        self.index["stats"]["last_reindex"] = datetime.now().isoformat()
        self._save_index()
        return {"indexed": count}

    def gc(self) -> dict:
        to_delete = []
        for mem_id, meta in self.index["entries"].items():
            if not (MEMORY_ROOT / meta["file"]).exists():
                to_delete.append(mem_id)
        for mem_id in to_delete:
            for tag in self.index["entries"].get(mem_id, {}).get("tags", []):
                if tag in self.index["tags"]:
                    self.index["tags"][tag] = [
                        x for x in self.index["tags"][tag] if x != mem_id]
            self.index["entries"].pop(mem_id, None)
        self.index["stats"]["last_gc"] = datetime.now().isoformat()
        self._save_index()
        return {"cleaned": len(to_delete), "remaining": len(self.index["entries"])}


if __name__ == "__main__":
    import sys
    mm = MemoryManager()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "gc":
        print(json.dumps(mm.gc(), ensure_ascii=False))
    elif cmd == "reindex":
        print(json.dumps(mm.reindex(), ensure_ascii=False))
    elif cmd == "recall":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        for r in mm.recall(query=query):
            print(f"[P{r['priority']}] {r['file']}: {r['summary']}")
    elif cmd == "stats":
        print(json.dumps(mm.index["stats"], ensure_ascii=False, indent=2))
    elif cmd == "remember":
        content = sys.argv[2]
        tags = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        mid = mm.remember(content, tags=tags)
        print(f"Stored: {mid}")
    else:
        print("Usage: memory_manager.py [gc|reindex|recall|stats|remember] [args...]")
