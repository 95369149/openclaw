#!/usr/bin/env python3
"""
task_classifier.py - 任务分类器
基于规则对任务文本做分类，输出 TaskMeta

用法:
  from runtime.task_classifier import classify
  meta = classify(text, session_id, model_id)
"""
from dataclasses import dataclass, field
from typing import Any
import re


@dataclass
class TaskMeta:
    session_id: str
    text: str
    model_id: str = "claude-sonnet"
    estimated_complexity: str = "low"       # low / medium / high
    requires_code: bool = False
    requires_multimodal: bool = False
    requires_external_research: bool = False
    risk_level: str = "normal"              # normal / high_config / high_arch / high_business
    route_mode: str = "FAST"               # SELF / FAST / FULL / HIGH_RISK_PENDING
    required_agents: list[str] = field(default_factory=list)
    enforce_review: bool = False
    project_tags: list[str] = field(default_factory=list)
    estimated_code_lines_gt: int = 0
    overrides: dict[str, Any] = field(default_factory=dict)


# 分类规则：(正则, 字段, 值, 权重)
RULES = [
    # 配置/安全 → high_config
    (r"openclaw\.json|配置文件|config|密钥|api.?key|credential|secret|回滚|rollback", "risk_level", "high_config", 10),
    # 架构/战略 → high_arch
    (r"架构|系统设计|architecture|方案设计|路线图|roadmap|战略|终审", "risk_level", "high_arch", 8),
    # 对外正式 → high_business
    (r"对外正式|发布|release|publish|正式文稿|对外报告", "risk_level", "high_business", 8),
    # 需要代码
    (r"代码|写个|实现|开发|脚本|函数|接口|bug|修复|fix|python|javascript|typescript", "requires_code", True, 6),
    # 需要多模态
    (r"图片|视频|截图|看图|photo|image|video|pdf|文档|长文", "requires_multimodal", True, 6),
    # 需要外部调研
    (r"搜索|调研|查一下|竞品|对标|外链|github|先调研|benchmark|情报", "requires_external_research", True, 6),
    # 代码量大
    (r"200行|200 lines|大改|全面重构|整个系统", "estimated_code_lines_gt", 201, 6),
]

# 强制 scout 条件
FORCE_SCOUT = [
    r"架构设计|系统级方案",
    r"竞品|对标|第三方框架|选型",
    r"先调研|先对标",
    r"外链|github\.com",
]

# 强制 guard 条件
FORCE_GUARD = [
    r"openclaw\.json|配置文件",
    r"密钥|api.?key|credential|secret",
    r"回滚|rollback|备份",
    r"新skill|新mcp|新依赖|npm install|pip install",
]

# 强制 kitt 条件
FORCE_KITT = [
    r"架构|系统设计|architecture",
    r"终审|review|审查",
    r"战略|路线图|roadmap",
    r"对外正式|正式文稿",
]


def classify(text: str, session_id: str = "default", model_id: str = "claude-sonnet") -> TaskMeta:
    t = text.lower()
    meta = TaskMeta(session_id=session_id, text=text, model_id=model_id)

    # 应用规则
    for pattern, field_name, value, _ in RULES:
        if re.search(pattern, t):
            setattr(meta, field_name, value)

    # 强制 scout
    for p in FORCE_SCOUT:
        if re.search(p, t):
            if "scout" not in meta.required_agents:
                meta.required_agents.append("scout")
            meta.requires_external_research = True

    # 强制 guard
    for p in FORCE_GUARD:
        if re.search(p, t):
            if "guard" not in meta.required_agents:
                meta.required_agents.append("guard")
            meta.risk_level = "high_config"
            meta.enforce_review = True

    # 强制 kitt
    for p in FORCE_KITT:
        if re.search(p, t):
            if "kitt" not in meta.required_agents:
                meta.required_agents.append("kitt")
            meta.enforce_review = True

    # 决定 route_mode
    if meta.risk_level in ("high_config", "high_arch", "high_business"):
        meta.route_mode = "FULL"
        meta.enforce_review = True
    elif meta.required_agents:
        meta.route_mode = "FULL"
    elif meta.requires_code or meta.requires_external_research:
        meta.route_mode = "FAST"
        meta.estimated_complexity = "medium"
    else:
        meta.route_mode = "SELF"

    return meta


if __name__ == "__main__":
    import sys
    import json
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "帮我写一个脚本"
    meta = classify(text)
    print(json.dumps({
        "route_mode": meta.route_mode,
        "risk_level": meta.risk_level,
        "required_agents": meta.required_agents,
        "enforce_review": meta.enforce_review,
        "requires_code": meta.requires_code,
        "requires_external_research": meta.requires_external_research,
    }, ensure_ascii=False, indent=2))
