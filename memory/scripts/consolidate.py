#!/usr/bin/env python3
"""
记忆整合器 v1.0
每日扫描 memory/shared/ 新文件，提取结构化信息，生成日摘要 + 更新 insights。
"""
import os
import sys
import json
import glob
from datetime import datetime, date

WORKSPACE = "/Users/apple/.openclaw/workspace"
SHARED_DIR = os.path.join(WORKSPACE, "memory/shared")
SUMMARIES_DIR = os.path.join(WORKSPACE, "memory/summaries")
INSIGHTS_DIR = os.path.join(WORKSPACE, "memory/insights")
CONSOLIDATION_DIR = os.path.join(WORKSPACE, "memory/consolidation")
RUNS_LOG = os.path.join(CONSOLIDATION_DIR, "runs.jsonl")
QUEUE_FILE = os.path.join(CONSOLIDATION_DIR, "queue.json")

def ensure_dirs():
    for d in [SUMMARIES_DIR, INSIGHTS_DIR, CONSOLIDATION_DIR]:
        os.makedirs(d, exist_ok=True)

def get_today():
    return date.today().isoformat()

def load_processed():
    """加载已处理文件列表"""
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return {"processed": []}

def save_processed(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_new_files(processed_list):
    """获取 shared/ 中未处理的文件"""
    all_files = glob.glob(os.path.join(SHARED_DIR, "*.md"))
    new = [f for f in all_files if os.path.basename(f) not in processed_list]
    return sorted(new, key=os.path.getmtime)

def extract_info(filepath):
    """从文件中提取结构化信息"""
    basename = os.path.basename(filepath)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 基础信息
    info = {
        "file": basename,
        "size": len(content),
        "lines": content.count("\n") + 1,
        "mtime": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
    }

    # 提取标题
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            info["title"] = line[2:].strip()
            break

    # 提取关键词（从文件名解析）
    parts = basename.replace(".md", "").split("_")
    if len(parts) >= 3:
        info["date"] = parts[0] if parts[0].startswith("202") else ""
        info["agent"] = parts[1] if len(parts) > 1 else ""
        info["topic"] = "_".join(parts[2:]) if len(parts) > 2 else ""

    # 提取主题标签
    tags = []
    keywords = {
        "培训": "training", "教材": "training",
        "配置": "config", "provider": "config",
        "agent": "agent", "Agent": "agent",
        "记忆": "memory", "整合": "memory",
        "SOP": "sop", "流程": "sop",
        "X进化": "learning", "学习": "learning",
        "工作总结": "summary", "日志": "summary",
        "急救": "emergency", "备份": "backup",
    }
    for kw, tag in keywords.items():
        if kw in content and tag not in tags:
            tags.append(tag)
    info["tags"] = tags

    # 提取结论/要点（找 ## 开头的段落）
    sections = []
    for line in content.split("\n"):
        if line.startswith("## "):
            sections.append(line[3:].strip())
    info["sections"] = sections[:10]

    return info

def generate_daily_summary(today, file_infos):
    """生成日摘要"""
    summary_path = os.path.join(SUMMARIES_DIR, f"{today}_daily-summary.md")

    lines = [f"# 日摘要 {today}\n"]
    lines.append(f"> 自动生成 | 处理文件数: {len(file_infos)}\n")

    # 按主题分组
    by_tag = {}
    for info in file_infos:
        for tag in info.get("tags", ["misc"]):
            by_tag.setdefault(tag, []).append(info)

    for tag, infos in sorted(by_tag.items()):
        lines.append(f"\n## {tag}")
        for info in infos:
            title = info.get("title", info["file"])
            lines.append(f"- **{title}** ({info['file']}, {info['lines']}行)")
            if info.get("sections"):
                for s in info["sections"][:5]:
                    lines.append(f"  - {s}")

    # 统计
    lines.append(f"\n## 统计")
    lines.append(f"- 总文件数: {len(file_infos)}")
    total_lines = sum(i["lines"] for i in file_infos)
    lines.append(f"- 总行数: {total_lines}")
    agents = set(i.get("agent", "") for i in file_infos if i.get("agent"))
    if agents:
        lines.append(f"- 涉及 Agent: {', '.join(agents)}")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return summary_path

def log_run(today, num_files, summary_path):
    """记录运行日志"""
    entry = {
        "ts": datetime.now().isoformat(),
        "date": today,
        "files_processed": num_files,
        "summary": os.path.basename(summary_path) if summary_path else None,
    }
    with open(RUNS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def main():
    ensure_dirs()
    today = get_today()
    queue = load_processed()
    processed = queue.get("processed", [])

    new_files = get_new_files(processed)
    if not new_files:
        print(f"[{today}] 没有新文件需要处理")
        log_run(today, 0, None)
        return

    print(f"[{today}] 发现 {len(new_files)} 个新文件")

    file_infos = []
    for fp in new_files:
        try:
            info = extract_info(fp)
            file_infos.append(info)
            processed.append(os.path.basename(fp))
            print(f"  ✓ {os.path.basename(fp)} ({info['lines']}行, tags={info.get('tags',[])})")
        except Exception as e:
            print(f"  ✗ {os.path.basename(fp)}: {e}")

    # 生成日摘要
    summary_path = generate_daily_summary(today, file_infos)
    print(f"日摘要已生成: {summary_path}")

    # 保存处理状态
    queue["processed"] = processed
    queue["last_run"] = datetime.now().isoformat()
    save_processed(queue)

    log_run(today, len(file_infos), summary_path)
    print(f"完成，处理了 {len(file_infos)} 个文件")

if __name__ == "__main__":
    main()
