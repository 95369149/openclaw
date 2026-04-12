#!/usr/bin/env python3
# memory/scripts/session_digest.py
# 自动从对话提取长期记忆（借鉴 OpenViking 的自动会话管理）

import json
import sys
from datetime import datetime
from pathlib import Path

def extract_long_term_memory(session_log: str) -> dict:
    """
    从会话日志中提取长期记忆
    
    提取规则：
    1. 用户明确表达的偏好/决策
    2. 重复出现的问题模式
    3. 成功/失败的操作记录
    4. 新学到的知识点
    """
    # TODO: 调用 LLM 做智能提取
    # 当前返回 mock 结构
    return {
        "timestamp": datetime.now().isoformat(),
        "session_id": "mock",
        "extracted": {
            "preferences": [],
            "decisions": [],
            "patterns": [],
            "learnings": []
        },
        "compressed_summary": "会话摘要（待实现）"
    }

def append_to_memory(memory_data: dict, target_file: Path):
    """追加到长期记忆文件"""
    with open(target_file, "a", encoding="utf-8") as f:
        f.write(f"\n## {memory_data['timestamp']}\n")
        f.write(f"{memory_data['compressed_summary']}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: session_digest.py <session_log_path>")
        sys.exit(1)
    
    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"Error: {log_path} not found")
        sys.exit(1)
    
    with open(log_path, "r", encoding="utf-8") as f:
        session_log = f.read()
    
    memory = extract_long_term_memory(session_log)
    
    # 写入 03_语义记忆/
    target = Path(__file__).parent.parent / "03_语义记忆" / "自动提取.md"
    append_to_memory(memory, target)
    
    print(f"✅ 长期记忆已提取并写入 {target}")
