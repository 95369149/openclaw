#!/usr/bin/env python3
"""
Kitt 进化引擎 — 统一入口 v1.0
整合所有子系统：记忆管理、模式学习、元认知、摘要生成、灵魂进化

用法:
    python evolve.py                → 完整进化周期（所有步骤）
    python evolve.py --dry-run      → 只分析不修改
    python evolve.py reindex        → 重建记忆索引
    python evolve.py gc             → 垃圾回收
    python evolve.py learn          → 模式学习
    python evolve.py check          → 元认知自检
    python evolve.py anomaly        → 异常检测
    python evolve.py summary        → L0 摘要索引
    python evolve.py inject         → 注入 L0/L1 摘要到文件
    python evolve.py soul           → SOUL.md 分析
    python evolve.py recall <query> → 记忆检索
    python evolve.py status         → 系统状态总览
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# 确保能 import 同目录模块
sys.path.insert(0, str(Path(__file__).parent))

from config import ENGINE_DATA_DIR
from memory_manager import MemoryManager
from pattern_extractor import PatternExtractor
from metacognition import Metacognition
from l0_summary import LayeredSummary
from soul_evolver import SoulEvolver


def pp(data):
    """Pretty print JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_full(dry_run=False):
    """完整进化周期"""
    print(f"🧬 Kitt 进化引擎启动 [{datetime.now().strftime('%Y-%m-%d %H:%M')}]")
    print(f"   模式: {'分析' if dry_run else '执行'}\n")

    report = {"timestamp": datetime.now().isoformat(), "dry_run": dry_run, "steps": {}}

    # 1. 重建索引
    print("① 重建记忆索引...")
    mm = MemoryManager()
    idx = mm.reindex()
    report["steps"]["reindex"] = idx
    print(f"   ✅ 索引 {idx['indexed']} 个文件\n")

    # 2. 垃圾回收
    print("② 垃圾回收...")
    gc = mm.gc()
    report["steps"]["gc"] = gc
    print(f"   ✅ 清理 {gc['cleaned']} 个孤立条目，剩余 {gc['remaining']}\n")

    # 3. 模式学习
    print("③ 模式学习...")
    pe = PatternExtractor()
    learn = pe.learn()
    report["steps"]["learn"] = learn
    print(f"   ✅ 处理 {learn.get('events_processed', 0)} 事件，"
          f"成功模式 {learn.get('success_patterns', 0)}，"
          f"失败模式 {learn.get('failure_patterns', 0)}\n")

    # 4. 元认知自检
    print("④ 元认知自检...")
    mc = Metacognition()
    check = mc.self_check()
    report["steps"]["metacognition"] = {
        "score": check["overall_score"],
        "status": check["status"],
    }
    print(f"   ✅ 综合评分: {check['overall_score']} ({check['status']})\n")

    # 5. 异常检测
    print("⑤ 异常检测...")
    anomalies = mc.detect_anomalies()
    report["steps"]["anomalies"] = {"count": len(anomalies)}
    if anomalies:
        for a in anomalies[:5]:
            print(f"   ⚠️  [{a['severity']}] {a['detail']}")
    else:
        print("   ✅ 无异常")
    print()

    # 6. L0 摘要索引
    print("⑥ L0 摘要索引...")
    ls = LayeredSummary()
    l0 = ls.build_index()
    report["steps"]["l0_index"] = l0
    print(f"   ✅ 索引 {l0['indexed']} 个文件\n")

    # 7. SOUL 分析
    print("⑦ SOUL.md 分析...")
    se = SoulEvolver()
    soul = se.analyze()
    report["steps"]["soul"] = {
        "issues": len(soul.get("issues", [])),
        "proposals": len(soul.get("proposals", [])),
    }
    if soul.get("issues"):
        for i in soul["issues"][:3]:
            print(f"   ⚠️  [{i['severity']}] {i['detail']}")
    else:
        print("   ✅ SOUL.md 状态良好")
    print()

    # 写入日志
    if not dry_run:
        log_file = ENGINE_DATA_DIR / "evolution_log.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(report, ensure_ascii=False) + "\n")

    # 总结
    score = check["overall_score"]
    emoji = "🟢" if score >= 0.85 else "🟡" if score >= 0.6 else "🔴"
    print(f"{'='*50}")
    print(f"{emoji} 进化完成 | 健康评分: {score} | 异常: {len(anomalies)}")
    print(f"{'='*50}")

    return report


def cmd_status():
    """系统状态总览"""
    mm = MemoryManager()
    stats = mm.index.get("stats", {})
    print("📊 Kitt 进化引擎状态")
    print(f"   记忆条目: {stats.get('total', '?')}")
    print(f"   上次索引: {stats.get('last_reindex', '从未')}")
    print(f"   上次 GC:  {stats.get('last_gc', '从未')}")

    log_file = ENGINE_DATA_DIR / "evolution_log.jsonl"
    if log_file.exists():
        lines = log_file.read_text().strip().split("\n")
        if lines:
            last = json.loads(lines[-1])
            print(f"   上次进化: {last.get('timestamp', '?')}")

    mc_file = ENGINE_DATA_DIR / "metacognition_reports.jsonl"
    if mc_file.exists():
        lines = mc_file.read_text().strip().split("\n")
        if lines:
            last = json.loads(lines[-1])
            print(f"   健康评分: {last.get('overall_score', '?')} ({last.get('status', '?')})")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    cmd = args[0] if args else "full"

    if cmd == "full":
        result = cmd_full(dry_run)
    elif cmd == "status":
        cmd_status()
    elif cmd == "reindex":
        pp(MemoryManager().reindex())
    elif cmd == "gc":
        pp(MemoryManager().gc())
    elif cmd == "learn":
        pp(PatternExtractor().learn())
    elif cmd == "check":
        report = Metacognition().self_check()
        pp(report)
        print(f"\n综合评分: {report['overall_score']} ({report['status']})")
    elif cmd == "anomaly":
        anomalies = Metacognition().detect_anomalies()
        for a in anomalies:
            print(f"  [{a['severity']}] {a['detail']}")
        if not anomalies:
            print("  无异常")
    elif cmd == "summary":
        pp(LayeredSummary().build_index())
    elif cmd == "inject":
        force = "--force" in sys.argv
        pp(LayeredSummary().inject_all(force))
    elif cmd == "soul":
        pp(SoulEvolver().analyze())
    elif cmd == "recall":
        query = args[1] if len(args) > 1 else ""
        # 同时搜索记忆索引和 L0 索引
        print("=== 记忆索引 ===")
        for r in MemoryManager().recall(query=query):
            print(f"  [P{r['priority']}] {r['file']}: {r['summary']}")
        print("\n=== L0 索引 ===")
        for r in LayeredSummary().quick_recall(query):
            print(f"  {r['path']}: {r['l0']}")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
