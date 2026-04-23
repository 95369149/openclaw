# memory/scripts/ — Kitt 脚本体系

## 统一入口

### `evolve.py` — 进化引擎（统一调度）
```bash
python evolve.py              # 完整进化周期
python evolve.py --dry-run    # 只分析不修改
python evolve.py status       # 系统状态总览
python evolve.py reindex      # 重建记忆索引
python evolve.py gc           # 垃圾回收
python evolve.py learn        # 模式学习
python evolve.py check        # 元认知自检
python evolve.py anomaly      # 异常检测
python evolve.py summary      # L0 摘要索引
python evolve.py inject       # 注入 L0/L1 摘要到文件头
python evolve.py soul         # SOUL.md 分析
python evolve.py recall <词>  # 记忆检索
```

### `sync.sh` — 统一同步（Git + iCloud）
```bash
bash sync.sh                  # 自动模式（Git备份 + iCloud latest）
bash sync.sh backup           # Git 备份
bash sync.sh restore          # 从 Git 恢复
bash sync.sh icloud           # iCloud 全量同步（含多agent）
bash sync.sh full             # 全量：Git + iCloud + 滚动备份
bash sync.sh weekly           # iCloud weekly 滚动备份
bash sync.sh monthly          # iCloud monthly 滚动备份
bash sync.sh agents           # 仅同步其他 agent
```

## 进化引擎模块

| 文件 | 职责 |
|------|------|
| `config.py` | 路径配置、参数常量 |
| `memory_manager.py` | 记忆索引、GC、recall、remember |
| `pattern_extractor.py` | 从执行日志提取成功/失败模式 |
| `metacognition.py` | 自检评分（7维度）、异常检测 |
| `l0_summary.py` | L0/L1/L2 三层摘要、快速检索 |
| `soul_evolver.py` | SOUL.md 分析、进化提案 |

调用关系：`evolve.py` → 调度以上所有模块

## 工具脚本

| 文件 | 职责 |
|------|------|
| `xjrouter_proxy.py` | xjrouter HTTP 反向代理（SSE聚合+流式透传） |
| `gateway-watchdog.sh` | Gateway 健康监控，崩溃自动重启 |
| `check-update.sh` | OpenClaw 版本更新检查 |

## 数据目录

`engine_data/` — 进化引擎运行数据（索引、日志、模式）
- `index.json` — 记忆索引
- `l0_index.json` — L0 摘要索引
- `evolution_log.jsonl` — 进化运行日志
- `metacognition_reports.jsonl` — 自检报告
- `anomalies.jsonl` — 异常记录
- `patterns/` — 模式数据

## 重构记录

2026-02-24: 首次重构，详见 `refactor_report.md`
