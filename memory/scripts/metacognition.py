"""
元认知模块 v3.1 — Kitt 的自我监控
严格评分标准，不自欺欺人
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from config import *


class Metacognition:
    def __init__(self):
        self.report_file = ENGINE_DATA_DIR / "metacognition_reports.jsonl"
        self.anomaly_file = ENGINE_DATA_DIR / "anomalies.jsonl"

    def self_check(self) -> dict:
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        report["checks"]["memory_health"] = self._check_memory_health()
        report["checks"]["rule_coverage"] = self._check_rule_coverage()
        report["checks"]["knowledge_freshness"] = self._check_knowledge_freshness()
        report["checks"]["log_continuity"] = self._check_log_continuity()
        report["checks"]["content_quality"] = self._check_content_quality()
        report["checks"]["rule_execution"] = self._check_rule_execution()
        report["checks"]["memory_coverage"] = self._check_memory_coverage()

        scores = [c.get("score", 0) for c in report["checks"].values()]
        report["overall_score"] = round(sum(scores) / len(scores), 2) if scores else 0

        if report["overall_score"] >= 0.85:
            report["status"] = "healthy"
        elif report["overall_score"] >= 0.6:
            report["status"] = "needs_attention"
        else:
            report["status"] = "critical"

        self._log(self.report_file, report)
        return report

    def _check_memory_health(self) -> dict:
        required_dirs = ["01_强制规则", "02_知识库", "03_语义记忆",
                         "05_日常日志", "07_版本控制", "10_项目"]
        missing = [d for d in required_dirs if not (MEMORY_ROOT / d).exists()]

        required_files = ["00_大脑中枢.md", "00_数字分身.md"]
        missing_files = [f for f in required_files if not (MEMORY_ROOT / f).exists()]

        # 检查索引文件
        index_dirs = ["01_强制规则", "02_知识库", "03_语义记忆",
                      "04_情景记忆", "80_收藏"]
        missing_index = [d for d in index_dirs
                         if (MEMORY_ROOT / d).exists()
                         and not (MEMORY_ROOT / d / "_INDEX.md").exists()]

        total_md = len([f for f in MEMORY_ROOT.rglob("*.md")
                        if "90_归档" not in str(f) and "scripts" not in str(f)])

        score = 1.0
        score -= 0.15 * len(missing)
        score -= 0.1 * len(missing_files)
        score -= 0.05 * len(missing_index)
        if total_md < 100:
            score -= 0.1

        return {
            "score": round(max(score, 0), 2),
            "total_files": total_md,
            "missing_dirs": missing,
            "missing_files": missing_files,
            "missing_index": missing_index,
        }

    def _check_rule_coverage(self) -> dict:
        critical_topics = {
            "排兵布阵": "agent 编制和路由",
            "记忆管理": "记忆读写规则",
            "安全": "配置变更安全",
            "Fallback": "模型降级链",
            "调度": "任务派发规则",
            "醒来自检": "compaction 后恢复",
            "频道": "渠道路由规则",
            "配置变更": "配置修改流程",
            "诚实": "行为约束",
            "防遗忘": "记忆断裂预防",
        }
        rules = [f.stem for f in RULES_DIR.glob("*.md")]
        covered = {}
        uncovered = {}
        for topic, desc in critical_topics.items():
            if any(topic in r for r in rules):
                covered[topic] = desc
            else:
                uncovered[topic] = desc

        score = len(covered) / len(critical_topics)
        return {
            "score": round(score, 2),
            "total_rules": len(rules),
            "covered": list(covered.keys()),
            "uncovered": list(uncovered.keys()),
        }

    def _check_knowledge_freshness(self) -> dict:
        now = datetime.now()
        stale_7d = []   # 7天没更新
        stale_30d = []  # 30天没更新
        fresh = 0

        for md in KNOWLEDGE_DIR.rglob("*.md"):
            mtime = datetime.fromtimestamp(md.stat().st_mtime)
            age = (now - mtime).days
            if age > 30:
                stale_30d.append(md.name)
            elif age > 7:
                stale_7d.append(md.name)
            else:
                fresh += 1

        total = fresh + len(stale_7d) + len(stale_30d)
        if total == 0:
            return {"score": 0, "fresh": 0, "stale_7d": 0, "stale_30d": 0}

        # 30天以上的严重扣分，7天的轻微扣分
        score = (fresh + len(stale_7d) * 0.5) / total
        return {
            "score": round(score, 2),
            "fresh": fresh,
            "stale_7d": len(stale_7d),
            "stale_30d": len(stale_30d),
            "stale_30d_files": stale_30d[:5],
        }

    def _check_log_continuity(self) -> dict:
        now = datetime.now()
        missing_days = []
        empty_days = []

        for i in range(7):
            day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            found = False
            for pattern in [f"{day}.md", f"2026-{day[5:]}.md", f"2025-{day[5:]}.md"]:
                log_file = DAILY_LOG_DIR / pattern
                if log_file.exists():
                    found = True
                    # 检查内容是否实质性（>200字）
                    content = log_file.read_text(encoding="utf-8", errors="ignore")
                    if len(content.strip()) < 200:
                        empty_days.append(day)
                    break
            if not found:
                missing_days.append(day)

        total_issues = len(missing_days) + len(empty_days) * 0.5
        score = max(1 - (total_issues * 0.15), 0)
        return {
            "score": round(score, 2),
            "missing_days": missing_days,
            "empty_days": empty_days,
        }

    def _check_content_quality(self) -> dict:
        """检查文件内容质量：空文件、过短文件、无标题文件"""
        empty = []
        too_short = []
        no_heading = []
        checked = 0

        skip_dirs = {"90_归档", "scripts", "黄金备份"}
        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if any(str(rel).startswith(s) for s in skip_dirs):
                continue
            checked += 1
            content = md.read_text(encoding="utf-8", errors="ignore").strip()

            if len(content) == 0:
                empty.append(str(rel))
            elif len(content) < 50:
                too_short.append(str(rel))
            elif not content.startswith("#"):
                no_heading.append(str(rel))

        if checked == 0:
            return {"score": 0, "checked": 0}

        bad = len(empty) + len(too_short) + len(no_heading) * 0.3
        score = max(1 - (bad / checked) * 2, 0)
        return {
            "score": round(score, 2),
            "checked": checked,
            "empty": empty[:5],
            "too_short": too_short[:5],
            "no_heading": no_heading[:5],
            "empty_count": len(empty),
            "too_short_count": len(too_short),
            "no_heading_count": len(no_heading),
        }

    def _check_rule_execution(self) -> dict:
        """检查规则是否真的在执行（有日志证据）"""
        execution_log = ENGINE_DATA_DIR / "agent_execution.jsonl"
        if not execution_log.exists():
            return {
                "score": 0.3,
                "reason": "无执行日志，无法验证规则执行情况",
                "has_log": False,
            }

        lines = execution_log.read_text(encoding="utf-8").strip().split("\n")
        events = []
        for line in lines:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        if len(events) < 10:
            return {
                "score": 0.4,
                "reason": f"执行日志仅 {len(events)} 条，数据不足",
                "has_log": True,
                "event_count": len(events),
            }

        # 检查是否覆盖了多个 bucket
        buckets = set(e.get("bucket", "unknown") for e in events)
        bucket_coverage = min(len(buckets) / 5, 1)  # 期望至少覆盖5个桶

        # 检查成功率
        success = sum(1 for e in events if e.get("success"))
        success_rate = success / len(events)

        score = bucket_coverage * 0.5 + success_rate * 0.5
        return {
            "score": round(score, 2),
            "has_log": True,
            "event_count": len(events),
            "bucket_coverage": list(buckets),
            "success_rate": round(success_rate, 2),
        }

    def _check_memory_coverage(self) -> dict:
        """检查关键事件是否有对应记忆"""
        now = datetime.now()
        # 检查最近3天的日志是否提到了关键事件
        key_events_found = 0
        key_events_total = 0

        for i in range(3):
            day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            log_found = False
            for pattern in [f"{day}.md", f"2026-{day[5:]}.md"]:
                log_file = DAILY_LOG_DIR / pattern
                if log_file.exists():
                    log_found = True
                    content = log_file.read_text(encoding="utf-8", errors="ignore")
                    key_events_total += 1

                    # 检查日志是否包含结构化内容
                    has_structure = any(marker in content for marker in
                                       ["## ", "### ", "- [", "✅", "❌", "完成", "待办"])
                    if has_structure and len(content) > 500:
                        key_events_found += 1
                    break

            if not log_found:
                key_events_total += 1  # 缺失也算一个事件

        if key_events_total == 0:
            return {"score": 0.3, "reason": "无近期日志"}

        score = key_events_found / key_events_total
        return {
            "score": round(score, 2),
            "days_checked": 3,
            "structured_logs": key_events_found,
            "total_expected": key_events_total,
        }

    def detect_anomalies(self) -> list:
        anomalies = []

        rule_count = len(list(RULES_DIR.glob("*.md")))
        if rule_count > 80:
            anomalies.append({
                "type": "rule_bloat",
                "severity": "warning",
                "detail": f"强制规则 {rule_count} 个，考虑精简",
            })

        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if str(rel).startswith("90_归档"):
                continue
            size = md.stat().st_size
            if size > 50000:
                anomalies.append({
                    "type": "large_file",
                    "severity": "info",
                    "detail": f"{rel} ({size//1024}KB) 考虑拆分",
                })

        # 检查同名文件（真冗余，排除 _INDEX.md）
        names = {}
        for md in MEMORY_ROOT.rglob("*.md"):
            rel = md.relative_to(MEMORY_ROOT)
            if any(str(rel).startswith(s) for s in ("90_归档", "scripts", "黄金备份")):
                continue
            if md.name == "_INDEX.md":
                continue
            if md.name in names:
                anomalies.append({
                    "type": "duplicate_file",
                    "severity": "warning",
                    "detail": f"同名文件: {md.name} → {names[md.name]} 和 {rel}",
                })
            else:
                names[md.name] = str(rel)

        for a in anomalies:
            a["detected_at"] = datetime.now().isoformat()
            self._log(self.anomaly_file, a)

        return anomalies

    def _log(self, file_path: Path, data: dict):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    mc = Metacognition()
    print("=== 自检报告 ===")
    report = mc.self_check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n综合评分: {report['overall_score']} ({report['status']})")
    print("\n=== 异常检测 ===")
    anomalies = mc.detect_anomalies()
    for a in anomalies:
        print(f"  [{a['severity']}] {a['detail']}")
    if not anomalies:
        print("  无异常")
