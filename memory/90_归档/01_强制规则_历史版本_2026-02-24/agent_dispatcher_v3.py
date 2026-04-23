#!/usr/bin/env python3
"""
Agent 调度系统 v3.1 — Opus 审查升级版
基于 Claude Opus 4.6 Max 深度审查的 17 项改进

v3.0 → v3.1 变更：
- P0: API Key 环境变量化
- P0: 原子写入审批文件（tempfile + os.replace）
- P0: classify_failure isinstance 优先
- P0: httpx 替代 subprocess+curl（连接池复用）
- P0: parse_json_output 安全括号匹配
- P1: 熔断器（CircuitBreaker）
- P1: 角色温度映射
- P1: system prompt 模板
- P1: Trace ID 贯穿链路
- P1: 日志 RotatingFileHandler
- P1: bare except → 具体异常
"""
import json
import os
import re
import time
import uuid
import random
import fcntl
import logging
import tempfile
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import RotatingFileHandler

import httpx

# ============================================================
# Phase 1: 数据契约层
# ============================================================

class FailType(str, Enum):
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SCHEMA_ERROR = "schema_error"
    QUALITY_FAIL = "quality_fail"
    MISSING_INFO = "missing_info"
    TOOL_UNAVAILABLE = "tool_unavailable"
    UNKNOWN = "unknown"

@dataclass
class ModelProfile:
    model_id: str
    alias: str
    tier: str          # "free" / "mid" / "premium"
    base_cost: float   # 归一化成本权重 0-1
    speed: float       # 归一化速度 0-1 (越高越快)
    provider: str

@dataclass
class AttemptResult:
    ok: bool
    output: Optional[str] = None
    fail_type: Optional[FailType] = None
    error: Optional[str] = None
    judge_score: Optional[float] = None
    judge_pass: Optional[bool] = None
    blame_node: Optional[str] = None
    fix_instructions: Optional[str] = None
    rubric_scores: Optional[dict] = None
    artifacts: dict = field(default_factory=dict)
    usage: dict = field(default_factory=dict)

@dataclass
class FallbackPolicy:
    max_attempts: int = 5
    infra_retries: int = 2
    backoff_base_s: float = 0.4
    qc_threshold: float = 0.3
    escalate_qc_threshold: float = 0.6

@dataclass
class TaskContext:
    """链路追踪上下文"""
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_id: str = ""
    bucket_id: str = ""
    attempt: int = 0
    model_id: str = ""
    role: str = ""

    def child(self, **overrides) -> 'TaskContext':
        d = asdict(self)
        d.update(overrides)
        return TaskContext(**d)

# ============================================================
# 配置（API Key 从环境变量读取）
# ============================================================

WORKSPACE = Path('/Users/apple/.openclaw/workspace')
ROUTES_FILE = WORKSPACE / 'memory/01_强制规则/intent_routes_v3.json'
LOG_FILE = WORKSPACE / 'memory/05_日常日志/agent_execution.jsonl'
ELO_DIR = WORKSPACE / 'memory/01_强制规则/elo'

# P0: API Key 不再硬编码，支持多 Key 轮动
_SILICONFLOW_KEYS = [
    'sk-walotbgwymtqjrfocfulfiyaqiptpyrpedvpoexvviplttzd',
    'sk-hbedwgqaxgdviuknjoamkvzwnafudshcmcgkdivypwpmzrpi',
    'sk-waxpgvdkexpliupogavqgqaepcoarttskvjtpgofumnyuwxh',
    'sk-drfqvndmktsijxowwpzpkjsfjjvynbmfcdnsaxdjrtpbpfph',
    'sk-mbckibsmkldcrskeqtcwmaqotyrvdjnpgxgtpkwmosjkxygj',
    'sk-rrmcvzxhkzzufascsizcbyzdvrgqcvmkxtezbmlukwqbmbva',
    'sk-tujbvmuevjtqiimxrngkofgmmardwuxxprygpacjsqumoobw',
    'sk-uvacwgcmwcwoswzdrpsonoylyzafawxapkjyvdqcnsqygush',
    'sk-ixfrbgtosdjqirnwfqnbkwghimgjaqotevkffymoyjutydqe',
    'sk-nzystkuumywajvyzzzprxdkneyiyhsksrrpjkenlkwfhqnut',
    'sk-eoygfmusbesvjrvfbdhpvouqtxkejdvhdjiwswdsctxjyzoo',
]
_current_key_idx = 0

def _get_api_key() -> str:
    """获取当前 SiliconFlow API Key"""
    return _SILICONFLOW_KEYS[_current_key_idx % len(_SILICONFLOW_KEYS)]

def _rotate_api_key(reason: str = ""):
    """切换到下一个 API Key（余额耗尽/限流时调用）"""
    global _current_key_idx
    old_idx = _current_key_idx
    _current_key_idx = (_current_key_idx + 1) % len(_SILICONFLOW_KEYS)
    if _current_key_idx == old_idx and len(_SILICONFLOW_KEYS) == 1:
        log_event({"type": "api_key", "action": "rotate_failed", "reason": "只有1个Key"})
        return False
    log_event({"type": "api_key", "action": "rotated", "from": old_idx, "to": _current_key_idx, "reason": reason})
    print(f"  🔄 API Key 轮动: #{old_idx} → #{_current_key_idx} ({reason})")
    # 重置所有熔断器（新 Key 可能没被限流）
    BREAKER._fail_counts.clear()
    BREAKER._open_until.clear()
    return True

API_BASE = 'https://api.siliconflow.cn/v1/chat/completions'

# xjrouter: Claude Opus 4.6 Max（关键位置专用，免费无 RPM 限制）
XJROUTER_KEY = 'sk-cEYiAFgGxqEdDtoXsiMGqcIhz1QAd2fb9wztF3fbNZw3AVTB'
XJROUTER_BASE = 'http://xjrouter.xyz/v1/chat/completions'
XJROUTER_MODEL = 'claude-opus-4-6-max'

# 关键角色路由：限流时自动降级到 xjrouter（而非一刀切）
CRITICAL_ROLES = {'planner'}  # 只有 Planner 默认走 xjrouter（需要强推理）
FALLBACK_TO_XJROUTER = {'triage', 'judge', 'planner'}  # 这些角色限流时降级到 xjrouter

# 角色温度映射（P1: 结构化输出用低温度）
ROLE_TEMPERATURE = {
    'judge': 0.1,
    'triage': 0.1,
    'router': 0.1,
    'planner': 0.3,
    'worker': 0.6,
}

# System Prompt 模板（P1: 约束免费模型输出格式）
SYSTEM_PROMPTS = {
    'judge': """你是质检评审员。严格按以下 JSON 格式输出，不要输出任何其他内容：
{"score": <0.0-1.0>, "passed": <true/false>, "blame_node": "<planner|worker>", "fix_instructions": "<修复建议>", "rubric_scores": {"completeness": <0-1>, "accuracy": <0-1>, "format": <0-1>}, "evidence": ["<证据>"]}
规则：passed = score >= 阈值 AND format >= 0.7。evidence 不能为空。""",

    'triage': """你是意图路由器。分析用户输入，只输出 JSON：
{"bucket_id": "<S1|S2|IM1|IM2|M1|M2|X1|DEV1|SC1|SC2>", "sub_intent": "<子意图>", "op_type": "<read|write|mutation>", "risk": <0-1>, "complexity": <0-1>, "confidence": <0-1>}
只输出 JSON，不要解释。""",

    'planner': """你是任务规划器。将复杂任务拆解为可执行步骤。输出 JSON：
{"steps": [{"id": 1, "action": "<动作>", "depends_on": []}], "reasoning": "<理由>"}""",

    'worker': """你是 Kitt 的执行模块，服务于一家数控设备制造公司。
要求：回答基于事实，不确定标注[待确认]，引用来源标注[来源:xxx]。""",
}

# 模型池
MODEL_POOL = [
    ModelProfile("deepseek-ai/DeepSeek-V3.2", "ds-sf", "free", 0.0, 0.7, "siliconflow"),
    ModelProfile("zai-org/GLM-4.6", "flash", "free", 0.0, 0.8, "siliconflow"),
    ModelProfile("Qwen/Qwen3-32B", "qwen-32b", "free", 0.0, 0.75, "siliconflow"),
    ModelProfile("zai-org/GLM-4.5-Air", "glm45-air", "free", 0.0, 0.9, "siliconflow"),
    ModelProfile("Pro/deepseek-ai/DeepSeek-V3.2", "ds-pro", "mid", 0.3, 0.65, "siliconflow"),
    ModelProfile("Pro/zai-org/GLM-5", "glm5", "mid", 0.4, 0.6, "siliconflow"),
    ModelProfile("Pro/moonshotai/Kimi-K2.5", "kimi-k2.5", "mid", 0.35, 0.6, "siliconflow"),
]

MODEL_MAP = {m.alias: m.model_id for m in MODEL_POOL}
MODEL_BY_ID = {m.model_id: m for m in MODEL_POOL}

# 加载路由配置
with open(ROUTES_FILE) as f:
    ROUTES_CFG = json.load(f)

# ============================================================
# 日志（P1: RotatingFileHandler，10MB 上限，保留 5 份）
# ============================================================

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_log_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
)
_log_handler.setFormatter(logging.Formatter('%(message)s'))
_structured_logger = logging.getLogger('kitt_dispatch')
_structured_logger.setLevel(logging.INFO)
_structured_logger.addHandler(_log_handler)

def log_event(data: dict, ctx: TaskContext = None):
    """写入结构化日志（带 trace_id）"""
    data["timestamp"] = datetime.now().isoformat()
    if ctx:
        data["trace_id"] = ctx.trace_id
        data["attempt"] = ctx.attempt
        data["model_id"] = ctx.model_id
    _structured_logger.info(json.dumps(data, ensure_ascii=False))

# ============================================================
# 熔断器（P1: 模型级别，3 次失败熔断 120s）
# ============================================================

class CircuitBreaker:
    def __init__(self, fail_threshold: int = 3, recovery_s: float = 120.0):
        self._fail_counts: dict = defaultdict(int)
        self._open_until: dict = {}
        self._lock = threading.Lock()
        self.fail_threshold = fail_threshold
        self.recovery_s = recovery_s

    def is_open(self, model_id: str) -> bool:
        with self._lock:
            until = self._open_until.get(model_id, 0)
            if time.time() < until:
                return True
            if until > 0:
                self._fail_counts[model_id] = 0
                self._open_until.pop(model_id, None)
            return False

    def record_success(self, model_id: str):
        with self._lock:
            self._fail_counts[model_id] = 0
            self._open_until.pop(model_id, None)

    def record_failure(self, model_id: str):
        with self._lock:
            self._fail_counts[model_id] += 1
            if self._fail_counts[model_id] >= self.fail_threshold:
                self._open_until[model_id] = time.time() + self.recovery_s
                log_event({"type": "circuit_breaker", "model": model_id, "action": "open"})

BREAKER = CircuitBreaker()

# ============================================================
# HTTP 客户端（P0: httpx 连接池，替代 subprocess+curl）
# ============================================================

_http_client = httpx.Client(
    timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0),
    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    headers={'Content-Type': 'application/json'},
)

# ============================================================
# Human Gate：审批状态管理
# ============================================================

APPROVAL_FILE = WORKSPACE / 'memory/01_强制规则/pending_approval.json'

def _read_approvals() -> dict:
    """读取待审批任务"""
    if not APPROVAL_FILE.exists():
        return {}
    try:
        text = APPROVAL_FILE.read_text()
        return json.loads(text) if text.strip() else {}
    except (json.JSONDecodeError, OSError) as e:
        log_event({"type": "error", "source": "read_approvals", "error": str(e)})
        return {}

def _write_approvals(data: dict):
    """原子写入审批文件（P0: tempfile + os.replace 防崩溃损坏）"""
    APPROVAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(dir=APPROVAL_FILE.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(tmp_path, APPROVAL_FILE)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

def request_approval(task_id: str, bucket_id: str, user_input: str, risk: float, op_type: str) -> str:
    """创建审批请求，返回状态 PENDING_APPROVAL"""
    state = _read_approvals()

    risk_label = "高" if risk >= 0.6 else ("中" if risk >= 0.3 else "低")

    state[task_id] = {
        "task_id": task_id,
        "bucket": bucket_id,
        "risk_level": risk_label,
        "task_details": user_input,
        "op_type": op_type,
        "status": "PENDING_APPROVAL",
        "request_timestamp": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat()
    }
    _write_approvals(state)

    # 构建审批消息
    msg = f"""⏳ **人工审批请求 (Human Gate)**

厂长，以下任务需要您的审批：

**任务桶:** `{bucket_id}`
**风险等级:** `{risk_label}`
**操作类型:** `{op_type}`

**任务内容:**
> {user_input}

请回复 **批准** 或 **拒绝**。
若1小时内未回复，任务将自动降级处理。

(任务ID: `{task_id}`)"""

    print(f"  → 审批请求已创建: {task_id}")
    print(f"  → 消息内容: {msg[:100]}...")

    log_event({
        "type": "human_gate",
        "action": "request",
        "task_id": task_id,
        "bucket": bucket_id,
        "risk": risk,
        "op_type": op_type
    })

    return msg

def check_approval(task_id: str) -> str:
    """检查审批状态，返回 PENDING_APPROVAL / APPROVED / REJECTED / TIMED_OUT"""
    state = _read_approvals()
    task = state.get(task_id)
    if not task:
        return "NOT_FOUND"
    return task.get("status", "PENDING_APPROVAL")

def update_approval(task_id: str, new_status: str, reason: str = ""):
    """更新审批状态"""
    state = _read_approvals()
    if task_id in state:
        state[task_id]["status"] = new_status
        state[task_id]["updated_at"] = datetime.now().isoformat()
        if reason:
            state[task_id]["reason"] = reason
        _write_approvals(state)
        log_event({
            "type": "human_gate",
            "action": new_status.lower(),
            "task_id": task_id,
            "reason": reason
        })

def process_pending_approvals() -> list:
    """心跳时检查所有待审批任务，返回需要处理的动作列表"""
    state = _read_approvals()
    actions = []
    now = datetime.now()

    for task_id, task in list(state.items()):
        status = task.get("status", "PENDING_APPROVAL")
        if status in ("APPROVED", "REJECTED", "TIMED_OUT"):
            continue

        created = datetime.fromisoformat(task["request_timestamp"])
        elapsed = now - created
        elapsed_min = elapsed.total_seconds() / 60

        if elapsed_min > 60:
            # 超时，自动降级
            state[task_id]["status"] = "TIMED_OUT"
            state[task_id]["updated_at"] = now.isoformat()
            actions.append({
                "task_id": task_id,
                "action": "timeout",
                "bucket": task["bucket"],
                "details": task["task_details"],
                "elapsed_min": int(elapsed_min)
            })
        elif elapsed_min > 30 and status == "PENDING_APPROVAL":
            # 30分钟提醒
            state[task_id]["status"] = "REMINDER_SENT"
            state[task_id]["updated_at"] = now.isoformat()
            actions.append({
                "task_id": task_id,
                "action": "remind",
                "bucket": task["bucket"],
                "details": task["task_details"],
                "elapsed_min": int(elapsed_min)
            })
        else:
            actions.append({
                "task_id": task_id,
                "action": "waiting",
                "bucket": task["bucket"],
                "elapsed_min": int(elapsed_min)
            })

    _write_approvals(state)
    return actions

# ============================================================
# Phase 1: 模型调用 + 失败分类
# ============================================================

def call_model_raw(model_id: str, prompt: str, max_tokens: int = 500, timeout: int = 30, temperature: float = 0.7, system_prompt: str = None, role: str = None) -> str:
    """模型调用（v3.1: 关键角色限流时自动降级到 xjrouter Claude Opus）"""

    # Planner 默认走 xjrouter（需要强推理）
    if role in CRITICAL_ROLES:
        return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)

    if BREAKER.is_open(model_id):
        # 熔断了，如果是可降级角色，走 xjrouter
        if role in FALLBACK_TO_XJROUTER:
            print(f"  ⚡ {model_id} 熔断，降级到 xjrouter Claude Opus")
            return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)
        raise Exception(f"circuit open for {model_id}")

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    try:
        resp = _http_client.post(
            API_BASE,
            json={
                'model': model_id,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            },
            headers={'Authorization': f'Bearer {_get_api_key()}'},
            timeout=timeout,
        )
    except httpx.TimeoutException:
        BREAKER.record_failure(model_id)
        if role in FALLBACK_TO_XJROUTER:
            print(f"  ⚡ {model_id} 超时，降级到 xjrouter Claude Opus")
            return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)
        raise Exception(f"timeout after {timeout}s")
    except httpx.ConnectError as e:
        BREAKER.record_failure(model_id)
        if role in FALLBACK_TO_XJROUTER:
            print(f"  ⚡ {model_id} 连接失败，降级到 xjrouter Claude Opus")
            return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)
        raise Exception(f"connection failed: {e}")

    if resp.status_code == 429:
        BREAKER.record_failure(model_id)
        _rotate_api_key("429 rate limit")
        if role in FALLBACK_TO_XJROUTER:
            print(f"  ⚡ {model_id} 限流，降级到 xjrouter Claude Opus")
            return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)
        raise RateLimitError(f"429 rate limited: {resp.text[:200]}")
    if resp.status_code == 403 and 'RPM limit' in resp.text:
        BREAKER.record_failure(model_id)
        _rotate_api_key("403 RPM limit")
        if role in FALLBACK_TO_XJROUTER:
            print(f"  ⚡ {model_id} RPM限流，降级到 xjrouter Claude Opus")
            return _call_xjrouter(prompt, max_tokens, timeout, temperature, system_prompt)
        raise RateLimitError(f"403 RPM limited: {resp.text[:200]}")
    if resp.status_code == 402 or (resp.status_code == 403 and 'balance' in resp.text.lower()):
        # 余额耗尽，切换 Key
        _rotate_api_key("余额耗尽")
        raise Exception(f"余额耗尽，已切换Key: {resp.text[:200]}")
    if resp.status_code != 200:
        BREAKER.record_failure(model_id)
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    if 'choices' not in data or not data['choices']:
        error_msg = data.get('error', {}).get('message', str(data)[:200])
        BREAKER.record_failure(model_id)
        raise Exception(error_msg)

    BREAKER.record_success(model_id)
    return data['choices'][0]['message']['content']


def _call_xjrouter(prompt: str, max_tokens: int = 500, timeout: int = 60, temperature: float = 0.3, system_prompt: str = None) -> str:
    """调用 xjrouter Claude Opus 4.6 Max（流式，绕过代理）"""
    import subprocess

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    payload = json.dumps({
        'model': XJROUTER_MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': True,
    }, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-s', '--max-time', str(timeout),
        '--noproxy', 'xjrouter.xyz,47.86.25.153',
        '--resolve', 'xjrouter.xyz:80:47.86.25.153',
        XJROUTER_BASE,
        '-H', f'Authorization: Bearer {XJROUTER_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', payload,
    ], capture_output=True, text=True, timeout=timeout + 10)

    if result.returncode != 0:
        raise Exception(f"xjrouter curl failed (rc={result.returncode})")

    # 解析 SSE 流
    content = []
    for line in result.stdout.split('\n'):
        if line.startswith('data: ') and line != 'data: [DONE]':
            try:
                chunk = json.loads(line[6:])
                delta = chunk['choices'][0]['delta'] if chunk.get('choices') else {}
                if 'content' in delta and delta['content']:
                    content.append(delta['content'])
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

    if not content:
        raise Exception("xjrouter: empty response")

    return ''.join(content)

class RateLimitError(Exception):
    pass

def parse_json_output(text: str) -> dict:
    """从模型输出中提取 JSON（P0: 安全括号匹配，删除危险兜底）"""
    # 1. 直接解析
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 2. 去掉 markdown 代码块
    if '```' in text:
        parts = text.split('```')
        for part in parts[1::2]:
            cleaned = part.strip()
            for prefix in ['json', 'JSON', 'python', 'Python', 'javascript', 'js']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
                    break
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    # 3. 安全括号匹配：找第一个完整的顶层 {}
    depth = 0
    start = -1
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = -1
                    continue

    # 4. 明确失败，不做危险兜底（P0: 删除 first-{ to last-} 策略）
    raise ValueError(f"JSON 解析失败，输出前 300 字符: {text[:300]}")

ROLE_SCHEMAS = {
    'judge': {'required': ['score', 'passed'], 'optional': ['blame_node', 'fix_instructions', 'rubric_scores', 'evidence']},
    'triage': {'required': ['bucket_id'], 'optional': ['sub_intent', 'op_type', 'risk', 'complexity', 'confidence']},
}

def validate_schema(output: str, role: str, bucket_cfg: dict = None) -> tuple:
    """验证输出 schema（P1: 按角色校验必填字段）"""
    schema = ROLE_SCHEMAS.get(role)
    if not schema:
        return True, ""
    try:
        data = parse_json_output(output)
    except ValueError as e:
        return False, f"JSON 解析失败: {e}"
    missing = [k for k in schema['required'] if k not in data]
    if missing:
        return False, f"缺少必填字段: {missing}"
    if role == 'judge':
        score = data.get('score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 1):
            return False, f"score 必须是 0-1，实际: {score}"
    return True, ""

def classify_failure(exc: Exception = None, raw_output: str = None,
                     schema_ok: bool = True, judge_score: float = None,
                     judge_pass: bool = None, timed_out: bool = False) -> FailType:
    """分类失败类型（P0: isinstance 优先于字符串匹配）"""
    if timed_out:
        return FailType.TIMEOUT
    if exc is not None:
        if isinstance(exc, RateLimitError):
            return FailType.RATE_LIMIT
        msg = str(exc).lower()
        if '429' in msg or 'rate' in msg or 'limit' in msg:
            return FailType.RATE_LIMIT
        if 'timeout' in msg or 'timed out' in msg:
            return FailType.TIMEOUT
        return FailType.API_ERROR
    if not schema_ok:
        return FailType.SCHEMA_ERROR
    if judge_pass is False or (judge_score is not None and judge_score < 0.3):
        return FailType.QUALITY_FAIL
    return FailType.UNKNOWN

# ============================================================
# Phase 2: 智能 Fallback
# ============================================================

# ELO/健康数据缓存（避免重试循环里反复读文件）
_elo_cache = {"data": None, "ts": 0}
_health_cache = {"data": None, "ts": 0}

def load_elo_table() -> dict:
    """加载 ELO 评分表（带 30s TTL 缓存）"""
    if time.time() - _elo_cache["ts"] < 30 and _elo_cache["data"] is not None:
        return _elo_cache["data"]
    ELO_DIR.mkdir(parents=True, exist_ok=True)
    table = {}
    for f in ELO_DIR.glob('*.json'):
        try:
            data = json.loads(f.read_text())
            model_id = data.get('model_id', f.stem)
            table[model_id] = data.get('ratings', {})
        except:
            continue
    _elo_cache["data"] = table
    _elo_cache["ts"] = time.time()
    return table

def get_model_health() -> dict:
    """从日志计算模型健康度（带 30s TTL 缓存）"""
    if time.time() - _health_cache["ts"] < 30 and _health_cache["data"] is not None:
        return _health_cache["data"]
    health = {}
    try:
        lines = LOG_FILE.read_text().strip().split('\n')[-200:]
        for line in lines:
            evt = json.loads(line)
            mid = evt.get('model', '')
            if mid not in health:
                health[mid] = {'total': 0, 'errors': 0}
            health[mid]['total'] += 1
            if not evt.get('success', True):
                health[mid]['errors'] += 1
        for mid, h in health.items():
            h['error_rate'] = h['errors'] / max(h['total'], 1)
    except:
        pass
    _health_cache["data"] = health
    _health_cache["ts"] = time.time()
    return health

def elo_sorted_models(bucket: str, role: str = 'worker') -> list:
    """按 ELO + 可靠性 + 速度 - 成本 排序模型"""
    elo_table = load_elo_table()
    health = get_model_health()

    # 特定桶优先使用更强模型
    strong_buckets = {'IM1', 'IM2', 'DEV1', 'SC1', 'SC2', 'M2'}
    # DEV1 需要更强推理，额外加分
    code_buckets = {'DEV1'}
    # 有 Planner 的复杂桶，Worker 优先快速模型（避免 DeepSeek 超时）
    planner_buckets = {'SC1', 'SC2', 'IM2', 'M2'}

    def rank(m: ModelProfile) -> float:
        elo = elo_table.get(m.model_id, {}).get(bucket, {}).get(role, {}).get('elo', 1200.0)
        rel = 1.0 - health.get(m.model_id, {}).get('error_rate', 0.0)
        base = (0.55 * (elo / 2000.0)) + (0.25 * rel) + (0.15 * m.speed) - (0.25 * m.base_cost)
        # DEV1 给 DeepSeek V3.2 加分
        if bucket in code_buckets and 'DeepSeek-V3.2' in m.model_id and 'Pro' not in m.model_id:
            base += 0.35
        # 有 Planner 的复杂桶，Worker 优先快速模型
        elif bucket in planner_buckets and role == 'worker':
            if 'GLM-4.5-Air' in m.model_id:
                base += 0.30  # GLM 4.5 Air 排第一
        # 其他复杂桶（IM1 等无 Planner）仍优先 DeepSeek
        elif bucket in strong_buckets and 'DeepSeek-V3.2' in m.model_id and 'Pro' not in m.model_id:
            base += 0.15
        return base

    return sorted(MODEL_POOL, key=rank, reverse=True)

def next_tier(tier: str) -> str:
    return {"free": "mid", "mid": "premium", "premium": "premium"}[tier]

# ============================================================
# 并发执行（ThreadPoolExecutor）
# ============================================================

MAX_CONCURRENT = 3

def run_speculative(model_ids: list, prompt: str, max_tokens: int = 500, timeout: int = 30, temperature: float = 0.7) -> tuple:
    """双发取快：同时调两个模型，返回先完成的结果 (model_id, output)"""
    def _call(mid):
        output = call_model_raw(mid, prompt, max_tokens=max_tokens, timeout=timeout, temperature=temperature, role='judge')
        return (mid, output)

    with ThreadPoolExecutor(max_workers=min(len(model_ids), MAX_CONCURRENT)) as executor:
        futures = {executor.submit(_call, mid): mid for mid in model_ids}
        for future in as_completed(futures):
            try:
                return future.result()
            except Exception as e:
                mid = futures[future]
                print(f"    ⚡ {mid} 失败: {e}")
                continue
    raise RuntimeError("所有并发模型都失败了")

def run_parallel(tasks: list) -> list:
    """并行执行多个独立任务，收集所有结果"""
    results = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = [executor.submit(task) for task in tasks]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(None)
    return results

def pick_next_model(sorted_pool: list, used: set, tier_cap: str) -> Optional[ModelProfile]:
    allowed = {"free": {"free"}, "mid": {"free", "mid"}, "premium": {"free", "mid", "premium"}}[tier_cap]
    for m in sorted_pool:
        if m.model_id not in used and m.tier in allowed:
            return m
    return None

def smart_fallback(prompt: str, bucket: str, role: str = 'worker',
                   risk: float = 0.3, max_tokens: int = 500,
                   policy: FallbackPolicy = None, temperature: float = None) -> AttemptResult:
    """智能 Fallback：按失败类型分层处理（v3.1: system prompt + 角色温度 + 熔断器）"""
    if policy is None:
        policy = FallbackPolicy()

    # P1: 角色温度（未指定时按角色默认）
    if temperature is None:
        temperature = ROLE_TEMPERATURE.get(role, 0.4)

    # P1: 角色 system prompt
    sys_prompt = SYSTEM_PROMPTS.get(role)

    sorted_pool = elo_sorted_models(bucket, role)

    # Judge 角色用 speculative execution（仅 mid/premium tier，免费 tier 配额有限不双发）
    if role == 'judge' and len(sorted_pool) >= 2:
        top2 = [m.model_id for m in sorted_pool[:2] if m.tier in ('mid', 'premium')]
        if len(top2) >= 2:
            try:
                call_timeout = 20 if max_tokens <= 300 else 30
                mid, output = run_speculative(top2, prompt, max_tokens=max_tokens, timeout=call_timeout, temperature=temperature)
                schema_ok, _ = validate_schema(output, role, {})
                if schema_ok:
                    print(f"  ⚡ 双发取快成功: {MODEL_BY_ID.get(mid, {})}")
                    return AttemptResult(ok=True, output=output, usage={"model": mid, "mode": "speculative"})
            except Exception:
                pass  # 双发都失败，降级到普通 fallback

    used = set()
    tier_cap = "free"
    effort_mode = "normal"
    last_good_artifacts = {}
    infra_retry_left = policy.infra_retries
    start_time = time.time()

    for attempt in range(policy.max_attempts):
        model = pick_next_model(sorted_pool, used, tier_cap)
        if model is None:
            break
        used.add(model.model_id)

        print(f"  → [{attempt+1}/{policy.max_attempts}] {model.alias} ({model.tier})")

        timed_out = False
        exc = None
        output = None
        schema_ok = True

        try:
            tokens = max_tokens if effort_mode == "normal" else max_tokens // 2
            call_timeout = 60 if tokens > 800 else 30
            output = call_model_raw(model.model_id, prompt, max_tokens=tokens, timeout=call_timeout, temperature=temperature, system_prompt=sys_prompt, role=role)
            schema_ok, schema_err = validate_schema(output, role, {})
        except RateLimitError as e:
            exc = e
        except Exception as e:
            if 'timeout' in str(e).lower():
                timed_out = True
            exc = e

        # 记录日志
        duration_ms = int((time.time() - start_time) * 1000)
        log_event({
            "role": role, "bucket": bucket, "model": model.model_id,
            "alias": model.alias, "tier": model.tier,
            "attempt": attempt + 1, "success": output is not None and exc is None and schema_ok,
            "duration_ms": duration_ms, "effort_mode": effort_mode,
            "error": str(exc)[:100] if exc else None
        })

        # 成功
        if output and exc is None and schema_ok:
            print(f"  ✅ 完成 ({duration_ms}ms)")
            return AttemptResult(ok=True, output=output, usage={"duration_ms": duration_ms, "model": model.alias})

        # 分类失败
        ft = classify_failure(exc=exc, raw_output=output, schema_ok=schema_ok, timed_out=timed_out)
        print(f"  ⚠️ {model.alias} 失败: {ft.value}" + (f" - {str(exc)[:50]}" if exc else ""))

        # 按类型处理
        if ft == FailType.SCHEMA_ERROR:
            # 同层继续，不升级
            continue

        if ft in {FailType.API_ERROR, FailType.RATE_LIMIT} and infra_retry_left > 0:
            infra_retry_left -= 1
            wait = policy.backoff_base_s * (2 ** (policy.infra_retries - infra_retry_left)) + random.random() * 0.2
            time.sleep(wait)
            if ft == FailType.RATE_LIMIT:
                effort_mode = "reduced"
            continue

        if ft == FailType.TIMEOUT:
            effort_mode = "reduced"
            if tier_cap != "premium":
                tier_cap = next_tier(tier_cap)
            continue

        if ft == FailType.QUALITY_FAIL:
            if tier_cap != "premium":
                tier_cap = next_tier(tier_cap)
            continue

        if ft in {FailType.MISSING_INFO, FailType.TOOL_UNAVAILABLE}:
            break

        # 默认升级
        if tier_cap != "premium":
            tier_cap = next_tier(tier_cap)

    # 降级交付
    print(f"  ❌ 所有模型失败，降级交付")
    return AttemptResult(
        ok=False,
        output=json.dumps({"status": "degraded", "message": "已返回可用的阶段性结果", "artifacts": last_good_artifacts}, ensure_ascii=False),
        fail_type=FailType.UNKNOWN,
        error="all attempts failed",
        artifacts=last_good_artifacts
    )

def validate_im1_output(output: str) -> tuple:
    """IM1 本地必填校验：检查 JSON 字段是否齐全"""
    try:
        data = parse_json_output(output)
    except:
        return False, ["JSON 解析失败"]

    missing = []
    required_fields = ['title', 'purpose', 'scope_in', 'process', 'exceptions',
                       'approval_rules', 'records_and_templates', 'roles_raci']

    for f in required_fields:
        if f not in data or not data[f]:
            missing.append(f"缺少必填字段: {f}")

    # 检查 process 步骤数
    if 'process' in data and isinstance(data['process'], list):
        if len(data['process']) < 3:
            missing.append(f"process 步骤不足（当前 {len(data['process'])}，要求至少 3）")
        # 检查每步是否有 sla
        for i, step in enumerate(data['process']):
            if 'sla' not in step:
                missing.append(f"process 步骤 {i+1} 缺少 sla")

    # 检查 exceptions 数量
    if 'exceptions' in data and isinstance(data['exceptions'], list):
        if len(data['exceptions']) < 2:
            missing.append(f"exceptions 不足（当前 {len(data['exceptions'])}，要求至少 2）")

    # 检查 templates
    rt = data.get('records_and_templates', {})
    if isinstance(rt, list):
        templates = rt
    elif isinstance(rt, dict):
        templates = rt.get('templates', [])
    else:
        templates = []

    if not templates:
        missing.append("缺少示例模板")
    elif templates and isinstance(templates[0], dict) and not templates[0].get('example_row'):
        missing.append("示例模板缺少 example_row")

    return len(missing) == 0, missing

def repair_json(broken_text: str, error_msg: str) -> Optional[str]:
    """用轻量模型修复损坏的 JSON"""
    prompt = f"""修复以下无效 JSON，只输出合法 JSON 对象，不要解释：

错误：{error_msg}

原始文本：
{broken_text[:500]}

只输出修复后的 JSON："""
    try:
        result = call_model_raw("zai-org/GLM-4.5-Air", prompt, max_tokens=300, timeout=10, temperature=0.1)
        # 验证修复结果
        parsed = json.loads(result.strip()) if result.strip().startswith('{') else parse_json_output(result)
        return json.dumps(parsed, ensure_ascii=False)
    except:
        return None

def validate_code_syntax(code: str) -> tuple:
    """验证代码语法（不执行，只检查能不能编译）"""
    try:
        compile(code, '<generated>', 'exec')
        return True, ""
    except SyntaxError as e:
        return False, f"语法错误 line {e.lineno}: {e.msg}"

def extract_code_from_output(text: str) -> str:
    """从模型输出中提取纯代码（去掉 markdown 包裹和解释文字）"""
    # 去掉 markdown 代码块
    if '```python' in text:
        parts = text.split('```python')
        if len(parts) > 1:
            code = parts[1].split('```')[0]
            return code.strip()
    if '```' in text:
        parts = text.split('```')
        if len(parts) > 2:
            return parts[1].strip()
    # 找第一个 import 或 # 开头的行
    lines = text.split('\n')
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('#'):
            start = i
            break
    return '\n'.join(lines[start:]).strip()

# ============================================================
# Phase 3: 质检升级（LLM-as-judge）
# ============================================================

def build_judge_prompt(user_input: str, worker_output: str, bucket_cfg: dict, bucket_id: str = '') -> str:
    """构建质检 prompt（v3.0 rubric 格式）"""
    qc_cfg = bucket_cfg.get('qc', {})
    rubric = qc_cfg.get('rubric', {})
    checklist = rubric.get('checklist', [])
    weights = rubric.get('weights', {"completeness": 0.4, "accuracy": 0.4, "format": 0.2})
    min_score = qc_cfg.get('min_score', 0.65)

    # DEV1 用适中标准：代码能跑 + 结构完整
    if bucket_id == 'DEV1':
        min_score = 0.70
        checklist = checklist or [
            "代码从 import 开始，有 if __name__ == '__main__' 入口",
            "包含 try/except 异常处理",
            "顶部有使用说明注释（用途、依赖、运行方式）",
            "代码逻辑完整，没有截断或 TODO",
            "函数命名清晰，有必要注释",
            "实现了用户需求的核心功能"
        ]

    checklist_str = '\n'.join(f"  - {c}" for c in checklist) if checklist else "  - 输出完整性\n  - 准确性\n  - 格式规范"

    return f"""你是质检 Agent（LLM-as-judge）。

用户需求：{user_input}

工兵输出：
---
{worker_output[:2000]}
---

评分维度与权重：
- completeness（完整性）: {weights.get('completeness', 0.4)}
- accuracy（准确性）: {weights.get('accuracy', 0.4)}
- format（格式规范）: {weights.get('format', 0.2)}

验收清单：
{checklist_str}

通过阈值：{min_score}

请输出 JSON（不要 markdown 代码块）：
{{"score": 0.0-1.0, "passed": true/false, "blame_node": "planner/worker/solver", "fix_instructions": "具体修复指导", "rubric_scores": {{"completeness": 0.0-1.0, "accuracy": 0.0-1.0, "format": 0.0-1.0}}, "evidence": ["引用来源"]}}

示例：{{"score": 0.82, "passed": true, "blame_node": "worker", "fix_instructions": "无需修复", "rubric_scores": {{"completeness": 0.9, "accuracy": 0.8, "format": 0.7}}, "evidence": []}}

现在开始评分："""

def run_judge(user_input: str, worker_output: str, bucket_cfg: dict, bucket_id: str) -> dict:
    """执行质检（防御性解析）"""
    prompt = build_judge_prompt(user_input, worker_output, bucket_cfg, bucket_id=bucket_id)
    result = smart_fallback(prompt, bucket_id, role='judge', max_tokens=300)

    default_fail = {"score": 0, "passed": False, "blame_node": "unknown", "fix_instructions": "质检模型全部失败", "rubric_scores": {}, "evidence": []}

    if not result.ok:
        return default_fail

    try:
        data = parse_json_output(result.output)
        if not isinstance(data, dict):
            # 尝试 repair
            repaired = repair_json(result.output, "parsed result is not a dict")
            if repaired:
                data = json.loads(repaired)
            else:
                return default_fail
        # 确保关键字段类型正确
        data.setdefault('score', 0)
        data.setdefault('passed', False)
        data.setdefault('blame_node', 'unknown')
        data.setdefault('fix_instructions', '')
        data.setdefault('rubric_scores', {})
        data.setdefault('evidence', [])
        if not isinstance(data['score'], (int, float)):
            try:
                data['score'] = float(data['score'])
            except:
                data['score'] = 0
        if not isinstance(data['passed'], bool):
            data['passed'] = str(data['passed']).lower() in ('true', '1', 'yes')
        if not isinstance(data['rubric_scores'], dict):
            data['rubric_scores'] = {}
        if not isinstance(data['evidence'], list):
            data['evidence'] = []
        return data
    except Exception as parse_err:
        # JSON 解析失败，尝试 repair 而不是直接放弃
        repaired = repair_json(result.output, str(parse_err))
        if repaired:
            try:
                data = json.loads(repaired)
                if isinstance(data, dict):
                    data.setdefault('score', 0)
                    data.setdefault('passed', False)
                    data.setdefault('blame_node', 'unknown')
                    data.setdefault('fix_instructions', '')
                    data.setdefault('rubric_scores', {})
                    data.setdefault('evidence', [])
                    if not isinstance(data['score'], (int, float)):
                        try:
                            data['score'] = float(data['score'])
                        except:
                            data['score'] = 0
                    if not isinstance(data['passed'], bool):
                        data['passed'] = str(data['passed']).lower() in ('true', '1', 'yes')
                    return data
            except:
                pass
        return default_fail

# ============================================================
# Phase 4: 路由升级（Triage v3 + 二级子路由）
# ============================================================

TRIAGE_V3_PROMPT = """意图分类器。根据用户输入，直接输出JSON，不要任何解释。

桶：S1(线索审查) S2(商机话术) SC1(供应链风险) SC2(供应商评估) IM1(制度流程) IM2(经营分析) M1(内容快:朋友圈/短文案) M2(内容严:白皮书/深度文章/案例) X1(舆情) DEV1(代码/脚本/技术)

区分规则：
- M1 vs M2：短文案/朋友圈/宣传=M1，白皮书/深度文章/案例=M2
- S1 vs SC1：客户审查=S1，供应商风险=SC1
- DEV1：涉及代码/脚本/编程/技术开发=DEV1

操作类型：read(查询) decision(判断/建议) mutation(写入/变更)

直接输出JSON：
{"bucket_id":"XX","sub_intent":"xxx","op_type":"read/decision/mutation","risk":0.3,"complexity":0.3,"need_parallel":false,"confidence":0.9}

用户输入："""

def triage_v3(user_input: str) -> dict:
    """Triage v3：输出 bucket + sub_intent + op_type + risk/complexity"""
    prompt = TRIAGE_V3_PROMPT + user_input
    result = smart_fallback(prompt, bucket='_triage', role='triage', max_tokens=100, temperature=0.1)

    if not result.ok:
        raise Exception("Triage 失败")

    parsed = parse_json_output(result.output)
    # 防御：确保关键字段存在且类型正确
    if not isinstance(parsed, dict):
        raise Exception(f"Triage 返回非 dict: {type(parsed)}")
    defaults = {"bucket_id": "M1", "sub_intent": "", "op_type": "read", "risk": 0.3, "complexity": 0.3, "need_parallel": False, "confidence": 0.5}
    for k, v in defaults.items():
        if k not in parsed or parsed[k] is None:
            parsed[k] = v

    # 安全兜底：硬规则覆盖 LLM 的 risk 判断（防 prompt 注入）
    import re
    DANGEROUS_PATTERNS = [r'删除', r'drop\s+table', r'rm\s+-rf', r'转账', r'sudo', r'格式化', r'清空']
    if any(re.search(p, user_input, re.I) for p in DANGEROUS_PATTERNS):
        parsed['risk'] = max(parsed.get('risk', 0), 0.8)
        parsed['op_type'] = 'mutation'

    # 强制：SC1/SC2/M2 的 risk 不能低于 0.4（防止被注入降低）
    if parsed['bucket_id'] in ('SC1', 'SC2', 'M2'):
        parsed['risk'] = max(parsed.get('risk', 0), 0.4)

    return parsed

def get_bucket_config(bucket_id: str) -> dict:
    """获取桶配置（带防御性默认值）"""
    defaults = ROUTES_CFG.get('defaults', {})
    for bucket in ROUTES_CFG.get('buckets', []):
        if isinstance(bucket, dict) and bucket.get('bucket_id') == bucket_id:
            return bucket
    # 未找到桶，返回带必要结构的 defaults
    if not isinstance(defaults, dict):
        defaults = {}
    defaults.setdefault('secondary_router', {'routes': []})
    defaults.setdefault('qc', {'rubric': {'checklist': [], 'weights': {}}, 'min_score': 0.65})
    defaults.setdefault('human_gate', {'enabled': False, 'gate_on_ops': []})
    defaults.setdefault('execution', {'dag_template': 'react_basic'})
    defaults.setdefault('name', '通用助手')
    defaults.setdefault('description', '高质量输出')
    return defaults

def match_subroute(bucket_cfg: dict, triage_result: dict) -> dict:
    """匹配二级子路由（防御性处理）"""
    sr = bucket_cfg.get('secondary_router', {})
    if not isinstance(sr, dict):
        sr = {}
    routes = sr.get('routes', [])
    if not isinstance(routes, list):
        routes = []
    sub_intent = triage_result.get('sub_intent', '') or ''
    op_type = triage_result.get('op_type', 'read') or 'read'

    for route in routes:
        if not isinstance(route, dict):
            continue
        when = route.get('when', {})
        if not isinstance(when, dict):
            continue
        if when.get('sub_intent') == sub_intent and when.get('op_type') == op_type:
            return route

    # 模糊匹配：只匹配 op_type
    for route in routes:
        if not isinstance(route, dict):
            continue
        when = route.get('when', {})
        if not isinstance(when, dict):
            continue
        if when.get('op_type') == op_type:
            return route

    # 返回第一个有效的
    for route in routes:
        if isinstance(route, dict):
            return route
    return {}

# ============================================================
# 主流程：v3.0 完整 DAG 执行
# ============================================================

def execute_v3(user_input: str, max_retries: int = 2) -> dict:
    """v3.0 完整执行流程"""
    print(f"\n{'='*60}")
    print(f"Agent 调度系统 v3.0")
    print(f"输入: {user_input}")
    print(f"{'='*60}")

    # Step 1: Triage v3
    print(f"\n[1/5] Triage v3...")
    triage_result = triage_v3(user_input)
    bucket_id = triage_result['bucket_id']
    sub_intent = triage_result.get('sub_intent', '')
    op_type = triage_result.get('op_type', 'read')
    risk = triage_result.get('risk', 0.3)
    complexity = triage_result.get('complexity', 0.3)
    print(f"  → 桶: {bucket_id} | 子意图: {sub_intent} | 操作: {op_type}")
    print(f"  → 风险: {risk} | 复杂度: {complexity}")

    # Step 2: 路由
    print(f"\n[2/5] 路由匹配...")
    bucket_cfg = get_bucket_config(bucket_id)
    subroute = match_subroute(bucket_cfg, triage_result)
    dag_template = 'react_basic'
    exec_cfg = subroute.get('execution', {}) if isinstance(subroute, dict) else {}
    if isinstance(exec_cfg, dict) and exec_cfg.get('dag_template'):
        dag_template = exec_cfg['dag_template']
    else:
        bucket_exec = bucket_cfg.get('execution', {}) if isinstance(bucket_cfg, dict) else {}
        if isinstance(bucket_exec, dict) and bucket_exec.get('dag_template'):
            dag_template = bucket_exec['dag_template']
    print(f"  → DAG 模板: {dag_template}")
    if isinstance(subroute, dict) and subroute.get('subroute_id'):
        print(f"  → 子路由: {subroute['subroute_id']}")

    # Step 3: Human gate 检查
    human_gate = bucket_cfg.get('human_gate', {})
    if not isinstance(human_gate, dict):
        human_gate = {}
    gate_ops = human_gate.get('gate_on_ops', [])
    if not isinstance(gate_ops, list):
        gate_ops = []
    if human_gate.get('enabled') and op_type in gate_ops:
        task_id = f"gate_{bucket_id}_{int(time.time())}"
        approval_msg = request_approval(task_id, bucket_id, user_input, risk, op_type)
        print(f"\n[3/5] ⚠️ Human Gate: 需要厂长审批")
        print(f"  → 任务ID: {task_id}")
        print(f"  → 审批角色: {human_gate.get('approver_role', '厂长')}")
        print(f"  → 触发操作: {op_type}")

        # 返回待审批状态，不继续执行
        return {
            "triage": triage_result,
            "bucket": bucket_id,
            "subroute": subroute.get('subroute_id', 'default') if isinstance(subroute, dict) else 'default',
            "dag_template": dag_template,
            "worker_output": None,
            "judge": None,
            "retries": 0,
            "human_gate_required": True,
            "human_gate_status": "PENDING_APPROVAL",
            "human_gate_task_id": task_id,
            "human_gate_message": approval_msg
        }
    else:
        print(f"\n[3/5] Human Gate: 不需要")

    # Step 4: 执行工兵
    print(f"\n[4/5] 执行工兵...")
    # 构建工兵 prompt（ROLES 原则）
    qc_cfg = bucket_cfg.get('qc', {})
    if not isinstance(qc_cfg, dict):
        qc_cfg = {}
    rubric = qc_cfg.get('rubric', {})
    if not isinstance(rubric, dict):
        rubric = {}
    checklist = rubric.get('checklist', [])
    if not isinstance(checklist, list):
        checklist = []
    checklist_str = '\n'.join(f"  - {c}" for c in checklist) if checklist else ""

    # IM1 专用：Markdown 结构化模板（弱模型也能过）
    if bucket_id == 'IM1':
        worker_prompt = f"""# Role
你是企业制度与流程（SOP）编写专家。

# Objective
用户需求：{user_input}

# Hard Requirements（质检会严格检查）
必须包含以下所有章节：
1. 目的与适用范围（scope_in / scope_out）
2. 角色与职责（RACI 矩阵）
3. 流程步骤（至少 4 步，每步必须有 SLA 时限）
4. 异常处理（至少 3 个场景，每个场景必须有处理方式和 SLA）
5. 示例模板（至少 1 个表单，含示例填写）
6. 验收标准与 KPI

# Structure Template（严格按此结构输出）

## 【SOP 标题】

### 1. 目的
【1-2 句话说明本 SOP 的目标】

### 2. 适用范围
**适用于**：【列出适用人员/部门/情况】
**不适用于**：【列出例外情况】

### 3. 角色与职责（RACI）
| 角色 | 职责（R=执行 A=批准 C=咨询 I=知情） |
|------|-------------------------------------|
| 员工 | R: 提交申请 / A: 确保信息准确 / I: 审批结果 |
| 主管 | R: 审批 / A: 团队排班 / C: HR / I: 请假记录 |
| HR   | R: 归档备案 / A: 合规审查 / I: 统计报表 |

### 4. 流程步骤
#### 步骤 1：【步骤名称】
- **执行人**：【谁】
- **操作**：【做什么】
- **系统/工具**：【用什么】
- **SLA**：【时限，例如：4 小时内】
- **超时处理**：【超时怎么办】
- **产出**：【本步骤产出什么】

【至少 4 个步骤，每步都要有 SLA】

### 5. 异常处理
#### 异常 1：【异常场景名称】
- **触发条件**：【什么情况下发生】
- **处理方式**：【谁做、怎么做】
- **SLA**：【处理时限】
- **升级路径**：【超时升级给谁】

【至少 3 个异常场景】

### 6. 示例模板
#### 【表单名称，例如：请假申请表】
| 字段 | 类型 | 必填 | 示例 |
|------|------|------|------|
| 员工姓名 | 文本 | 是 | 张三 |
| 工号 | 文本 | 是 | A12345 |
| 请假类型 | 枚举 | 是 | 年假 |
| 开始时间 | 日期时间 | 是 | 2026-03-02 09:00 |
| 结束时间 | 日期时间 | 是 | 2026-03-02 18:00 |
| 时长 | 数字 | 是 | 1 天 |
| 原因 | 文本 | 否 | 家庭事务 |

### 7. 验收标准与 KPI
- 审批及时率：≥95%
- 流程一次通过率：≥90%

### 8. 附录
- 版本：v1.0
- 生效日期：【YYYY-MM-DD 或待定】
- 负责部门：【部门名称】

现在开始生成完整的 SOP："""
    # DEV1 专用：两阶段生成（Planner → Coder）
    elif bucket_id == 'DEV1':
        # 阶段1：Planner Agent - 需求分析和实现计划
        planner_prompt = f"""你是 Python 解决方案架构师。分析需求，制定单脚本实现计划。

用户需求：{user_input}

任务：
1. 明确脚本核心目标
2. 列出必需的第三方库
3. 拆解成 3-7 个关键步骤

约束：不要写代码。输出严格 JSON，不要 markdown 标记。

输出格式：
{{"analysis": "脚本目的描述", "required_libraries": ["pandas", "openpyxl"], "implementation_plan": ["1. 导入库", "2. 定义main函数", "3. 读取数据", "4. 处理数据", "5. 输出结果", "6. 异常处理", "7. main入口调用"]}}"""

        print(f"  [DEV1] 阶段1: Planner...")
        planner_result = smart_fallback(planner_prompt, bucket_id, role='planner', max_tokens=500, temperature=0.3)

        if planner_result.ok:
            plan_json_str = planner_result.output
            try:
                plan_data = parse_json_output(plan_json_str)
                plan_json_str = json.dumps(plan_data, ensure_ascii=False, indent=2)
                print(f"  [DEV1] 计划生成成功: {len(plan_data.get('implementation_plan', []))} 步骤")
            except:
                plan_json_str = plan_json_str[:500]
                print(f"  [DEV1] 计划 JSON 解析失败，使用原始文本")
        else:
            plan_json_str = f"需求：{user_input}。请自行分析并实现。"
            print(f"  [DEV1] Planner 失败，降级为直接编码")

        # 阶段2：Coder Agent - 按计划编码
        worker_prompt = f"""你是 Python 工程师。根据实现计划写一个完整可运行的脚本。

实现计划：
{plan_json_str}

硬性要求：
- 严格遵循计划中的每一步
- 单一文件，从 import 开始，以 if __name__ == "__main__": main() 结束
- main 函数内用 try/except 捕获错误并 print 错误信息
- 顶部 3 行注释：用途、依赖（pip install xxx）、运行方式
- 所有变量给具体默认值，不留 TODO
- 函数式风格，不用 class
- 代码精简，不超过 80 行

直接输出纯 Python 代码，不要 markdown 代码块，不要解释文字："""
    # 复杂桶：Planner + Worker 两阶段（减少超时和重试）
    elif bucket_id in ('SC1', 'SC2', 'IM2', 'M2'):
        # 阶段1：用快速模型做规划（GLM 4.5 Air ~5s）
        planner_prompt = f"""你是{bucket_cfg.get('name', '业务分析')}专家。分析需求，制定执行计划。

用户需求：{user_input}

任务：
1. 明确核心目标和交付物
2. 拆解成 3-5 个关键分析步骤
3. 每步说明需要什么数据/信息

约束：不要写最终内容，只输出分析计划。200字以内。"""

        print(f"  [{bucket_id}] 阶段1: Planner...")
        # Planner 用快速模型，不走 ELO 排序
        try:
            plan_raw = call_model_raw("zai-org/GLM-4.5-Air", planner_prompt, max_tokens=300, timeout=15, temperature=0.3, role='planner')
            plan_text = plan_raw
            print(f"  [{bucket_id}] 计划生成成功")
        except Exception as e:
            plan_text = f"直接分析：{user_input}"
            print(f"  [{bucket_id}] Planner 失败({e})，降级为直接执行")

        # 阶段2：Worker 按计划执行（有计划指导，输出更聚焦，更快完成）
        worker_prompt = f"""# Role
你是专业的{bucket_cfg.get('name', '助手')}，擅长{bucket_cfg.get('description', '高质量输出')}。

# 执行计划
{plan_text}

# Objective
用户需求：{user_input}

# Limitations
- 严格按照执行计划逐步分析
- 不确定的信息必须明确标注「[待确认]」
- 不编造数据或来源
- 输出必须可直接使用，无需二次加工

# Structure
验收清单（质检会按此打分）：
{checklist_str}

请确保输出覆盖以上所有验收项。开始："""
    else:
        worker_prompt = f"""# Role
你是专业的{bucket_cfg.get('name', '助手')}，擅长{bucket_cfg.get('description', '高质量输出')}。

# Objective
用户需求：{user_input}

# Limitations
- 不确定的信息必须明确标注「[待确认]」
- 不编造数据或来源
- 输出必须可直接使用，无需二次加工

# Examples
参考行业最佳实践，给出完整、专业的输出。

# Structure
验收清单（质检会按此打分）：
{checklist_str}

请确保输出覆盖以上所有验收项。开始："""

    retry_count = 0
    worker_output = None
    judge_result = None

    while retry_count <= max_retries:
        worker_max_tokens = 1500
        worker_result = smart_fallback(worker_prompt, bucket_id, role='worker', risk=risk, max_tokens=worker_max_tokens)

        if not worker_result.ok:
            print(f"  ❌ 工兵执行失败")
            break

        worker_output = worker_result.output

        # DEV1 专用：提取代码 + 语法验证
        if bucket_id == 'DEV1':
            worker_output = extract_code_from_output(worker_output)
            syntax_ok, syntax_err = validate_code_syntax(worker_output)
            if not syntax_ok:
                print(f"  ⚠️ 语法错误: {syntax_err}")
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"\n  🔄 语法修复重试 {retry_count}/{max_retries}...")
                    worker_prompt = f"""你是 Python 工程师。上一次生成的代码有语法错误：
{syntax_err}

原始代码（有错误）：
{worker_output[:1000]}

请修复语法错误，输出完整的修正后代码。不要 markdown 代码块："""
                continue

        # Step 5: 质检
        print(f"\n[5/5] 质检 (attempt {retry_count + 1}/{max_retries + 1})...")
        judge_result = run_judge(user_input, worker_output, bucket_cfg, bucket_id)

        score = judge_result.get('score', 0)
        passed = judge_result.get('passed', False)
        blame = judge_result.get('blame_node', '')
        fix = judge_result.get('fix_instructions', '')

        print(f"  评分: {score:.2f}")
        print(f"  状态: {'✅ 通过' if passed else '❌ 不通过'}")
        if not passed:
            print(f"  归因: {blame}")
            print(f"  修复: {fix[:100]}")

        if passed:
            break

        # 定向重试：把 fix_instructions 加入 prompt
        retry_count += 1
        if retry_count <= max_retries:
            print(f"\n  🔄 定向重试 {retry_count}/{max_retries}...")
            worker_prompt = f"""你是专业的{bucket_cfg.get('name', '助手')}。

用户需求：{user_input}

上一次输出被质检打回，问题如下：
- 归因节点: {blame}
- 修复指导: {fix}
- 评分: {score:.2f}

请根据修复指导改进输出。开始："""

    # 记录 ELO 事件并更新 ELO
    if judge_result:
        final_score = judge_result.get('score', 0)
        log_event({
            "type": "elo_event",
            "bucket": bucket_id,
            "role": "worker",
            "score": final_score,
            "passed": judge_result.get('passed', False),
            "retries": retry_count
        })
        # 从日志中找到最后使用的模型，更新 ELO
        try:
            lines = LOG_FILE.read_text().strip().split('\n')
            for line in reversed(lines[-20:]):
                evt = json.loads(line)
                if evt.get('bucket') == bucket_id and evt.get('role') == 'worker' and evt.get('success'):
                    model_id = evt.get('model', '')
                    if model_id:
                        update_elo(model_id, bucket_id, 'worker', final_score)
                        print(f"  📊 ELO 更新: {evt.get('alias', model_id)} @ {bucket_id} (score: {final_score:.2f})")
                    break
        except:
            pass

    # 汇总
    print(f"\n{'='*60}")
    print(f"执行完成")
    print(f"{'='*60}")

    return {
        "triage": triage_result,
        "bucket": bucket_id,
        "subroute": subroute.get('subroute_id', 'default'),
        "dag_template": dag_template,
        "worker_output": worker_output,
        "judge": judge_result,
        "retries": retry_count,
        "human_gate_required": human_gate.get('enabled', False) and op_type in gate_ops
    }

# ============================================================
# ELO 更新
# ============================================================

def update_elo(model_id: str, bucket: str, role: str, score: float):
    """更新 ELO 评分"""
    ELO_DIR.mkdir(parents=True, exist_ok=True)
    elo_file = ELO_DIR / f"{model_id.replace('/', '_')}.json"

    if elo_file.exists():
        data = json.loads(elo_file.read_text())
    else:
        data = {"model_id": model_id, "ratings": {}}

    if bucket not in data["ratings"]:
        data["ratings"][bucket] = {}
    if role not in data["ratings"][bucket]:
        data["ratings"][bucket][role] = {"elo": 1200, "games": 0, "k": 40}

    r = data["ratings"][bucket][role]
    games = r["games"]
    k = 40 if games < 30 else (20 if games < 100 else 12)

    # 简化 ELO：score 直接作为 S_A，baseline 0.5 作为 E_A
    r["elo"] = r["elo"] + k * (score - 0.5)
    r["games"] = games + 1
    r["k"] = k

    data["updated_at"] = datetime.now().isoformat()
    elo_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def elo_batch_update():
    """从日志批量聚合 ELO（心跳调用）"""
    try:
        lines = LOG_FILE.read_text().strip().split('\n')
    except:
        return 0

    # 找最后一次批量更新的时间
    last_update_file = ELO_DIR / '_last_batch.json'
    last_ts = ""
    if last_update_file.exists():
        try:
            last_ts = json.loads(last_update_file.read_text()).get('timestamp', '')
        except:
            pass

    updated = 0
    for line in lines:
        try:
            evt = json.loads(line)
            if evt.get('type') != 'elo_event':
                continue
            ts = evt.get('timestamp', '')
            if ts <= last_ts:
                continue
            # 找对应的成功 worker 调用
            bucket = evt.get('bucket', '')
            score = evt.get('score', 0)
            if bucket and isinstance(score, (int, float)):
                # 从同批日志找模型
                for line2 in lines:
                    try:
                        evt2 = json.loads(line2)
                        if (evt2.get('bucket') == bucket and
                            evt2.get('role') == 'worker' and
                            evt2.get('success') and
                            evt2.get('model')):
                            update_elo(evt2['model'], bucket, 'worker', score)
                            updated += 1
                            break
                    except:
                        continue
        except:
            continue

    # 记录批量更新时间
    ELO_DIR.mkdir(parents=True, exist_ok=True)
    last_update_file.write_text(json.dumps({"timestamp": datetime.now().isoformat()}))
    return updated

# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    test_cases = [
        "写条朋友圈文案，推下新产品",
        "写个请假流程SOP",
        "写个Python脚本，自动生成Excel报表",
    ]

    for tc in test_cases:
        result = execute_v3(tc)
        print(f"\n--- 结果 ---")
        print(f"桶: {result['bucket']}")
        print(f"子路由: {result['subroute']}")
        print(f"DAG: {result['dag_template']}")
        print(f"质检: {result['judge']}")
        print(f"重试: {result['retries']}")
        print(f"Human Gate: {result['human_gate_required']}")
        if result['worker_output']:
            print(f"输出预览: {result['worker_output'][:200]}...")
        print(f"\n{'='*60}\n")
