"""
L0/L1/L2 三层摘要生成器 — 防失忆核心机制
L0: 一句话摘要（compaction 后快速恢复）
L1: 核心信息（5-10行，足够判断上下文）
L2: 完整内容（原文）

为每个 md 文件在头部注入 L0/L1 摘要注释
"""
import json
import re
from pathlib import Path
from datetime import datetime
from config import *


class LayeredSummary:
    def __init__(self):
        self.index_file = ENGINE_DATA_DIR / "l0_index.json"

    def generate_l0(self, content: str, filename: str) -> str:
        """从内容提取一句话摘要"""
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not lines:
            return f"{filename}: 空文件"

        # 优先用 # 标题
        for line in lines:
            if line.startswith("# ") and not line.startswith("##"):
                return line[2:].strip()

        # 其次用第一行非空内容
        first = lines[0]
        if first.startswith(">"):
            first = first.lstrip("> ").strip()
        return first[:80]

    def generate_l1(self, content: str, max_lines: int = 8) -> str:
        """提取核心信息（标题+关键要点）"""
        lines = content.split("\n")
        l1_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # 收集标题和要点
            if stripped.startswith("#"):
                l1_lines.append(stripped)
            elif stripped.startswith("- **") or stripped.startswith("1."):
                l1_lines.append(stripped)
            elif "✅" in stripped or "❌" in stripped or "→" in stripped:
                l1_lines.append(stripped)

            if len(l1_lines) >= max_lines:
                break

        return "\n".join(l1_lines) if l1_lines else content[:300]

    def inject_summary(self, file_path: Path, force: bool = False) -> bool:
        """在文件头部注入 L0/L1 摘要注释"""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # 已有摘要且不强制更新则跳过
        if content.startswith("<!-- L0:") and not force:
            return False

        # 去掉旧摘要
        content = re.sub(r'^<!-- L0:.*?-->\n?', '', content, flags=re.DOTALL)
        content = re.sub(r'^<!-- L1:.*?-->\n?', '', content, flags=re.DOTALL)

        l0 = self.generate_l0(content, file_path.name)
        l1 = self.generate_l1(content)

        header = f"<!-- L0: {l0} -->\n<!-- L1:\n{l1}\n-->\n"
        file_path.write_text(header + content, encoding="utf-8")
        return True

    def build_index(self) -> dict:
        """为所有 md 文件生成 L0 索引"""
        index = {"generated_at": datetime.now().isoformat(), "entries": {}}
        skip = {"90_归档", "scripts", "黄金备份"}

        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if any(str(rel).startswith(s) for s in skip):
                continue

            content = md.read_text(encoding="utf-8", errors="ignore")
            # 跳过已有 L0 注释的，直接提取
            l0_match = re.match(r'^<!-- L0: (.+?) -->', content)
            if l0_match:
                l0 = l0_match.group(1)
            else:
                l0 = self.generate_l0(content, md.name)

            index["entries"][str(rel)] = {
                "l0": l0,
                "size": len(content),
                "mtime": datetime.fromtimestamp(md.stat().st_mtime).isoformat(),
            }

        self.index_file.write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"indexed": len(index["entries"])}

    def inject_all(self, force: bool = False) -> dict:
        """为所有文件注入 L0/L1 摘要"""
        skip = {"90_归档", "scripts", "黄金备份"}
        injected = 0
        skipped = 0

        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if any(str(rel).startswith(s) for s in skip):
                continue
            if self.inject_summary(md, force):                injected += 1
            else:
                skipped += 1

        # 同时更新索引
        idx = self.build_index()
        return {"injected": injected, "skipped": skipped, "indexed": idx["indexed"]}

    def quick_recall(self, query: str, top_k: int = 10) -> list:
        """基于 L0 索引快速检索"""
        if not self.index_file.exists():
            self.build_index()

        index = json.loads(self.index_file.read_text(encoding="utf-8"))
        query_lower = query.lower()
        results = []

        for path, meta in index["entries"].items():
            l0 = meta["l0"].lower()
            if query_lower in l0 or query_lower in path.lower():
                results.append({"path": path, "l0": meta["l0"], "size": meta["size"]})

        results.sort(key=lambda x: x["size"], reverse=True)
        return results[:top_k]


if __name__ == "__main__":
    import sys
    ls = LayeredSummary()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "index"

    if cmd == "index":
        r = ls.build_index()
        print(json.dumps(r, ensure_ascii=False))
    elif cmd == "inject":
        force = "--force" in sys.argv
        r = ls.inject_all(force=force)
        print(json.dumps(r, ensure_ascii=False))
    elif cmd == "recall":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        for r in ls.quick_recall(query):
            print(f"  {r['path']}: {r['l0']}")
    else:
        print("Usage: l0_summary.py [index|inject|inject --force|recall <query>]")
