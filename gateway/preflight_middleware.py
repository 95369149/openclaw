#!/usr/bin/env python3
"""
preflight_middleware.py - 完整请求入口链路
把 bootstrap / classify / policy_engine / review_gate 串成一条链

用法:
  from gateway.preflight_middleware import PreflightMiddleware
  mid = PreflightMiddleware()
  meta = mid.handle(req)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

BASE_DIR = Path("/Users/apple/.openclaw/workspace")
sys.path.insert(0, str(BASE_DIR))

from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.review_gate import ReviewGate

# 灰度开关（改这里控制哪些 gate 生效）
ENABLE_MEMORY_BOOTSTRAP = True
ENABLE_REVIEW_GATE = True


@dataclass
class SimpleContext:
    system: str = ""

    def inject_system(self, text: str):
        self.system = (self.system + "\n" + text).strip() if self.system else text


class PreflightMiddleware:
    def __init__(
        self,
        bootstrap: Optional[BootstrapManager] = None,
        policy: Optional[PolicyEngine] = None,
        review_gate: Optional[ReviewGate] = None,
    ):
        self.bootstrap = bootstrap or BootstrapManager()
        self.policy = policy or PolicyEngine()
        self.review_gate = review_gate or ReviewGate()

    def handle(self, req: Any, ctx: Optional[SimpleContext] = None) -> Any:
        """
        主链路：preflight → bootstrap → classify → policy → review → return meta

        req 需要有：
          - session_id: str
          - text: str
          - model_id: str (可选，默认 claude-sonnet)
        """
        session_id = getattr(req, "session_id", "default")
        model_id = getattr(req, "model_id", "claude-sonnet")
        text = getattr(req, "text", "")

        if ctx is None:
            ctx = SimpleContext()

        # 1. memory bootstrap
        if ENABLE_MEMORY_BOOTSTRAP:
            self.bootstrap.ensure_bootstrapped(session_id, model_id, ctx)

        # 2. classify
        meta = classify(text, session_id, model_id)

        # 3. policy
        meta = self.policy.apply(meta)

        # 4. review gate
        if ENABLE_REVIEW_GATE and meta.enforce_review:
            draft = {"text": text, "session_id": session_id}
            self.review_gate.review_and_finalize(draft, meta)
            meta.enforce_review = False  # 已过审，不重复

        return meta


if __name__ == "__main__":
    @dataclass
    class FakeReq:
        session_id: str
        text: str
        model_id: str = "claude-sonnet"

    mid = PreflightMiddleware()

    tests = [
        ("帮我写一段 Python 脚本", "FAST"),
        ("修改 openclaw.json 路由规则，记得先备份", "FULL"),
        ("调研竞品振动刀切割机", "FULL"),
        ("设计分布式系统架构", "FULL"),
    ]

    for text, expected_route in tests:
        req = FakeReq(session_id="test-sess", text=text)
        try:
            meta = mid.handle(req)
            ok = meta.route_mode == expected_route
            print(f"{'✅' if ok else '❌'} [{text[:25]}] route={meta.route_mode} agents={meta.required_agents}")
        except RuntimeError as e:
            print(f"⚠️  [{text[:25]}] blocked: {e}")
