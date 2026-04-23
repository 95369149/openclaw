#!/usr/bin/env python3
"""
policy_engine.py - 策略引擎
读 config/policy.yml，对 TaskMeta 做最终决策：
- risk_level / enforce_review / required_agents / route_mode

用法:
  from runtime.policy_engine import PolicyEngine
  engine = PolicyEngine()
  meta = engine.apply(meta)
"""
from __future__ import annotations

import sys
from typing import Optional
from pathlib import Path
import yaml

WORKSPACE = Path("/Users/apple/.openclaw/workspace")
DEFAULT_POLICY_PATH = WORKSPACE / "config/policy.yml"


class PolicyEngine:
    def __init__(self, policy_path: str = str(DEFAULT_POLICY_PATH)):
        self.policy_path = Path(policy_path)
        self._rules: list[dict] = []
        self._defaults: dict = {}
        self._load()

    def _load(self):
        if not self.policy_path.exists():
            print(f"[policy_engine] warning: {self.policy_path} not found")
            return
        data = yaml.safe_load(self.policy_path.read_text(encoding="utf-8")) or {}
        self._defaults = data.get("defaults", {})
        self._rules = data.get("rules", [])

    def _match(self, meta, rule_match: dict) -> bool:
        for k, v in rule_match.items():
            meta_val = getattr(meta, k, None)
            if meta_val != v:
                return False
        return True

    def apply(self, meta):
        # 先用 defaults 填充（不覆盖已有高风险值）
        if not meta.route_mode or meta.route_mode == "PENDING":
            meta.route_mode = self._defaults.get("route_mode", "FAST")
        if not meta.enforce_review:
            meta.enforce_review = bool(self._defaults.get("enforce_review", False))

        # 逐条规则匹配
        for rule in self._rules:
            if self._match(meta, rule.get("match", {})):
                then = rule.get("then", {})
                # required_agents
                for a in then.get("require_agents", []):
                    if a not in meta.required_agents:
                        meta.required_agents.append(a)
                # enforce_review
                if "enforce_review" in then:
                    meta.enforce_review = bool(then["enforce_review"])
                # route_mode
                if "route_mode" in then:
                    meta.route_mode = then["route_mode"]
                # risk_level
                if "risk_level" in then:
                    meta.risk_level = then["risk_level"]

        return meta


if __name__ == "__main__":
    sys.path.insert(0, str(WORKSPACE))
    from runtime.task_classifier import classify

    tests = [
        ("修改 openclaw.json 的路由规则", "high_config", ["guard"], "FULL"),
        ("设计分布式系统架构", "high_arch", ["kitt"], "FULL"),
        ("调研竞品振动刀切割机", "normal", ["scout"], "FULL"),
        ("帮我写一段 Python 脚本", "normal", ["deep"], "FAST"),
    ]

    engine = PolicyEngine()
    for text, exp_risk, exp_agents, exp_route in tests:
        meta = classify(text)
        meta = engine.apply(meta)
        ok = (
            meta.risk_level == exp_risk
            and all(a in meta.required_agents for a in exp_agents)
            and meta.route_mode == exp_route
        )
        status = "✅" if ok else "❌"
        print(f"{status} [{text[:20]}] risk={meta.risk_level} agents={meta.required_agents} route={meta.route_mode}")
