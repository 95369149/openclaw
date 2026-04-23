"""
SOUL 进化器 — Kitt 的灵魂自动迭代
基于数据驱动优化 SOUL.md 中的规则和行为准则
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from config import *


class SoulEvolver:
    def __init__(self):
        self.changelog = ENGINE_DATA_DIR / "soul_changelog.jsonl"
        self.proposals_dir = VERSION_DIR
        self.soul_path = SOUL_FILE

    def analyze(self) -> dict:
        """分析当前 SOUL.md，生成优化建议"""
        if not self.soul_path.exists():
            return {"error": "SOUL.md not found"}

        soul_content = self.soul_path.read_text(encoding="utf-8")
        report = {
            "timestamp": datetime.now().isoformat(),
            "soul_size": len(soul_content),
            "sections": self._parse_sections(soul_content),
            "issues": [],
            "proposals": [],
        }

        # 检查规则一致性
        report["issues"] += self._check_consistency(soul_content)

        # 检查是否有过时内容
        report["issues"] += self._check_staleness(soul_content)

        # 基于模式数据生成优化建议
        report["proposals"] = self._generate_proposals(report["issues"])

        return report

    def _parse_sections(self, content: str) -> list:
        sections = []
        current = None
        for line in content.split("\n"):
            if line.startswith("## "):
                if current:
                    sections.append(current)
                current = {"title": line[3:].strip(), "lines": 0, "rules": 0}
            elif current:
                current["lines"] += 1
                if line.strip().startswith(("- ", "1.", "2.", "3.", "4.", "5.", "6.", "7.")):
                    current["rules"] += 1
        if current:
            sections.append(current)
        return sections

    def _check_consistency(self, content: str) -> list:
        issues = []

        # 检查是否引用了不存在的文件
        file_refs = re.findall(r'`(memory/[^`]+)`', content)
        for ref in file_refs:
            full_path = SOUL_FILE.parent / ref
            if not full_path.exists():
                issues.append({
                    "type": "broken_reference",
                    "severity": "medium",
                    "detail": f"SOUL.md 引用了不存在的文件: {ref}",
                })

        # 检查是否有矛盾的指令
        if "不废话" in content and "详细解释" in content:
            issues.append({
                "type": "contradiction",
                "severity": "low",
                "detail": "同时要求'不废话'和'详细解释'，可能矛盾",
            })

        return issues

    def _check_staleness(self, content: str) -> list:
        issues = []

        # 检查版本号
        version_match = re.search(r'v(\d+\.\d+)', content)
        if version_match:
            # 检查 SOUL.md 最后修改时间
            mtime = datetime.fromtimestamp(self.soul_path.stat().st_mtime)
            if datetime.now() - mtime > timedelta(days=14):
                issues.append({
                    "type": "stale_soul",
                    "severity": "medium",
                    "detail": f"SOUL.md 已 {(datetime.now() - mtime).days} 天未更新",
                })

        # 检查是否提到已废弃的概念
        deprecated = ["Jimmy", "workspace-kitt"]
        for term in deprecated:
            if term in content:
                issues.append({
                    "type": "deprecated_reference",
                    "severity": "low",
                    "detail": f"SOUL.md 仍提到 '{term}'，可能需要更新",
                })

        return issues

    def _generate_proposals(self, issues: list) -> list:
        proposals = []

        for issue in issues:
            if issue["type"] == "broken_reference":
                proposals.append({
                    "action": "fix_reference",
                    "priority": "medium",
                    "description": f"修复断链: {issue['detail']}",
                    "auto_fixable": False,
                    "risk": "low",
                })
            elif issue["type"] == "stale_soul":
                proposals.append({
                    "action": "refresh_soul",
                    "priority": "medium",
                    "description": "更新 SOUL.md 版本号和内容",
                    "auto_fixable": False,
                    "risk": "medium",
                })
            elif issue["type"] == "deprecated_reference":
                proposals.append({
                    "action": "update_reference",
                    "priority": "low",
                    "description": issue["detail"],
                    "auto_fixable": True,
                    "risk": "low",
                })

        return proposals

    def propose(self, title: str, changes: str, risk: str = "low") -> str:
        """生成进化提案，写入版本控制目录"""
        now = datetime.now()
        filename = f"进化提案_{now.strftime('%Y-%m-%d')}.md"
        filepath = self.proposals_dir / filename

        proposal = f"""# 进化提案 {now.strftime('%Y-%m-%d')}

## 提案: {title}
- 生成时间: {now.isoformat()}
- 风险等级: {risk}
- 状态: 待审批

## 变更内容
{changes}

## 风险评估
- 风险等级: {risk}
- 回滚方案: git revert 或从 iCloud 黄金备份恢复

## 审批
- [ ] 厂长审批
"""
        filepath.write_text(proposal, encoding="utf-8")

        # 记录 changelog
        entry = {
            "timestamp": now.isoformat(),
            "title": title,
            "risk": risk,
            "file": str(filepath.relative_to(MEMORY_ROOT)),
            "status": "pending",
        }
        with open(self.changelog, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return str(filepath)

    def apply(self, proposal_file: Path, approved: bool = False) -> dict:
        """应用已审批的提案（需厂长审批）"""
        if not approved:
            return {"status": "rejected", "reason": "需要厂长审批"}

        # 读取提案内容，这里只记录状态变更
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": str(proposal_file),
            "status": "applied",
        }
        with open(self.changelog, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return {"status": "applied", "file": str(proposal_file)}


if __name__ == "__main__":
    import sys
    se = SoulEvolver()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    if cmd == "analyze":
        result = se.analyze()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "propose":
        title = sys.argv[2] if len(sys.argv) > 2 else "自动优化提案"
        path = se.propose(title, "自动生成的优化建议")
        print(f"提案已生成: {path}")
    else:
        print("Usage: soul_evolver.py [analyze|propose] [title]")
