"""
模式提取器 v3.0 — Kitt 的学习引擎
从执行日志中提取成功/失败模式、模型偏好
"""
import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from config import *


class PatternExtractor:
    def __init__(self):
        self.success_file = PATTERNS_DIR / "success.jsonl"
        self.failure_file = PATTERNS_DIR / "failure.jsonl"
        self.model_prefs_file = ENGINE_DATA_DIR / "model_prefs.json"

    def parse_execution_logs(self, log_file: Path = None) -> list:
        log_file = log_file or EXECUTION_LOG
        events = []
        if not log_file.exists():
            return events
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def extract_success_patterns(self, events: list) -> list:
        combos = defaultdict(lambda: {"success": 0, "fail": 0,
                                       "total_latency": 0, "samples": []})
        for e in events:
            key = (e.get("bucket", "unknown"), e.get("model", "unknown"))
            if e.get("success"):
                combos[key]["success"] += 1
            else:
                combos[key]["fail"] += 1
            combos[key]["total_latency"] += e.get("latency_ms", 0)
            if len(combos[key]["samples"]) < 3:
                combos[key]["samples"].append({
                    "input": (e.get("input") or "")[:200],
                    "output": (e.get("output") or "")[:200],
                })

        patterns = []
        for (bucket, model), stats in combos.items():
            total = stats["success"] + stats["fail"]
            if total < MIN_PATTERN_OCCURRENCES:
                continue
            sr = stats["success"] / total
            pattern = {
                "bucket": bucket, "model": model,
                "success_rate": round(sr, 3),
                "avg_latency_ms": round(stats["total_latency"] / total),
                "sample_count": total,
                "extracted_at": datetime.now().isoformat(),
            }
            if sr >= PATTERN_CONFIDENCE_THRESHOLD:
                patterns.append(pattern)
                self._append_jsonl(self.success_file, pattern)
        return patterns

    def extract_failure_patterns(self, events: list) -> list:
        error_groups = defaultdict(list)
        for e in events:
            if not e.get("success") and e.get("error"):
                err_key = self._normalize_error(e["error"])
                error_groups[err_key].append(e)

        patterns = []
        for err_key, group in error_groups.items():
            if len(group) < MIN_PATTERN_OCCURRENCES:
                continue
            buckets = Counter(e.get("bucket", "?") for e in group)
            models = Counter(e.get("model", "?") for e in group)
            pattern = {
                "error_type": err_key,
                "occurrence_count": len(group),
                "common_buckets": dict(buckets.most_common(3)),
                "common_models": dict(models.most_common(3)),
                "extracted_at": datetime.now().isoformat(),
                "avoidance_hint": f"bucket={buckets.most_common(1)[0][0]} 时避免 {models.most_common(1)[0][0]}",
            }
            patterns.append(pattern)
            self._append_jsonl(self.failure_file, pattern)
        return patterns

    def update_model_preferences(self, events: list) -> dict:
        prefs = {}
        if self.model_prefs_file.exists():
            prefs = json.loads(self.model_prefs_file.read_text(encoding="utf-8"))

        bucket_stats = defaultdict(lambda: defaultdict(
            lambda: {"wins": 0, "losses": 0, "latency_sum": 0, "count": 0}))

        for e in events:
            bucket = e.get("bucket", "unknown")
            model = e.get("model", "unknown")
            s = bucket_stats[bucket][model]
            s["count"] += 1
            s["latency_sum"] += e.get("latency_ms", 0)
            if e.get("success"):
                s["wins"] += 1
            else:
                s["losses"] += 1

        for bucket, models in bucket_stats.items():
            rankings = []
            for model, s in models.items():
                if s["count"] < 2:
                    continue
                sr = s["wins"] / s["count"]
                avg_lat = s["latency_sum"] / s["count"]
                elo = round(1000 + sr * 500 - (avg_lat / 1000) * 50)
                rankings.append({
                    "model": model, "elo": elo,
                    "success_rate": round(sr, 3),
                    "avg_latency_ms": round(avg_lat),
                    "sample_count": s["count"],
                })
            rankings.sort(key=lambda x: x["elo"], reverse=True)
            prefs[bucket] = rankings

        prefs["_updated_at"] = datetime.now().isoformat()
        self.model_prefs_file.write_text(
            json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
        return prefs

    def _normalize_error(self, error: str) -> str:
        error = re.sub(r'[0-9a-f]{8,}', '<ID>', error)
        error = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '<TS>', error)
        error = re.sub(r'\d{3,}', '<NUM>', error)
        return error[:200]

    def _append_jsonl(self, file_path: Path, data: dict):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def learn(self, log_file: Path = None) -> dict:
        events = self.parse_execution_logs(log_file)
        if not events:
            return {"status": "no_logs", "events": 0}
        success_p = self.extract_success_patterns(events)
        failure_p = self.extract_failure_patterns(events)
        model_prefs = self.update_model_preferences(events)
        return {
            "status": "ok",
            "events_processed": len(events),
            "success_patterns": len(success_p),
            "failure_patterns": len(failure_p),
            "model_rankings_updated": len(model_prefs) - 1,
        }


if __name__ == "__main__":
    import sys
    pe = PatternExtractor()
    log_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    result = pe.learn(log_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
