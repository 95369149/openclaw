#!/usr/bin/env python3
"""
review_gate.py - 审核链门禁
高风险任务输出前强制过审，返回 approve / deny / pending

用法:
  from runtime.review_gate import ReviewGate
  gate = ReviewGate()
  result = gate.review(draft, meta)
  # result: {"status": "approve"/"deny"/"pending", "reason": "..."}
"""
from __future__ import annotations

import sys
import json
import subprocess
from typing import Optional, Any
from pathlib import Path

WORKSPACE = Path("/Users/apple/.openclaw/workspace")

# 风险等级 → 审核者映射
RISK_REVIEWER_MAP = {
    "high_config": "guard",
    "high_arch": "kitt",
    "high_business": "kitt",
}

# 免审条件
SKIP_REVIEW_AGENTS = {"kitt"}  # kitt 本身就是审核者，不自审


class ReviewGate:
    def __init__(self):
        # 可扩展：接入真实 agent 调用
        pass

    def review(self, draft: Any, meta, agent_id: str = "jimmy") -> dict:
        """
        主入口：判断是否需要审核，返回三态结果
        - approve: 通过
        - deny: 拒绝（附原因）
        - pending: 需要人工确认
        """
        # 1. 不需要审核
        if not getattr(meta, "enforce_review", False):
            return {"status": "approve", "reason": "enforce_review=false，无需审核"}

        # 2. 免审 agent（kitt 不自审）
        if agent_id in SKIP_REVIEW_AGENTS:
            return {"status": "approve", "reason": f"{agent_id} 是审核者，免审"}

        # 3. 根据风险等级决定审核者
        reviewer = RISK_REVIEWER_MAP.get(meta.risk_level)
        if not reviewer:
            return {"status": "approve", "reason": f"risk_level={meta.risk_level} 无对应审核者"}

        # 4. 调用审核逻辑
        return self._do_review(draft, meta, reviewer)

    def _do_review(self, draft: Any, meta, reviewer: str) -> dict:
        """
        实际审核逻辑
        当前版本：规则审核（不调用 LLM）
        后续可扩展为：调用 guard/kitt agent
        """
        checks = []

        # guard 审核：配置变更必须有备份计划
        if reviewer == "guard":
            text = getattr(meta, "text", "")
            if "openclaw.json" in text and "备份" not in text and "backup" not in text.lower():
                checks.append("配置变更未提及备份方案")
            if "密钥" in text or "api_key" in text.lower():
                checks.append("涉及密钥操作，需人工确认")

        # kitt 审核：架构/业务判断
        if reviewer == "kitt":
            required_agents = getattr(meta, "required_agents", [])
            if "scout" not in required_agents and meta.risk_level == "high_arch":
                checks.append("架构设计未经 scout 侦察，建议先调研")

        if checks:
            # 有问题但不是硬拒绝 → pending
            return {
                "status": "pending",
                "reviewer": reviewer,
                "reason": "；".join(checks),
                "action": f"请 {reviewer} 确认后继续",
            }

        return {
            "status": "approve",
            "reviewer": reviewer,
            "reason": f"{reviewer} 规则检查通过",
        }

    def review_and_finalize(self, draft: Any, meta, agent_id: str = "jimmy") -> Any:
        """
        审核通过返回 draft，拒绝抛异常，pending 返回 pending 状态
        """
        result = self.review(draft, meta, agent_id)
        if result["status"] == "deny":
            raise RuntimeError(f"[review_gate] DENIED by {result.get('reviewer','?')}: {result['reason']}")
        if result["status"] == "pending":
            raise RuntimeError(f"[review_gate] PENDING: {result['reason']} → {result.get('action','')}")
        return draft


if __name__ == "__main__":
    sys.path.insert(0, str(WORKSPACE))
    from runtime.task_classifier import classify
    from runtime.policy_engine import PolicyEngine

    engine = PolicyEngine()
    gate = ReviewGate()

    tests = [
        ("帮我写一段 Python 脚本", "approve"),
        ("修改 openclaw.json 路由规则，记得先备份", "approve"),
        ("修改 openclaw.json 路由规则", "pending"),
        ("设计分布式系统架构", "pending"),
    ]

    for text, expected in tests:
        meta = classify(text)
        meta = engine.apply(meta)
        draft = {"content": "draft output"}
        try:
            gate.review_and_finalize(draft, meta)
            status = "approve"
        except RuntimeError as e:
            msg = str(e)
            status = "pending" if "PENDING" in msg else "deny"

        ok = status == expected
        print(f"{'✅' if ok else '❌'} [{text[:30]}] → {status} (expected {expected})")
