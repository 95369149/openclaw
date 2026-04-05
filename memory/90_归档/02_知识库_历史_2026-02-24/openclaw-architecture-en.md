# OpenClaw Configuration Architecture (2026-02-19)

## System Overview
- Version: OpenClaw 2026.2.14
- Deployment: Local Mac (M1 16GB)
- Purpose: Manufacturing enterprise (Red Sun CNC) AI assistant + automated learning pipeline

## Four-Role Division System

| Role | Model | Responsibility | Cost | Notes |
|---|---|---|---|---|
| Daily Worker | Claude Sonnet 4.6 (mynewapi) | Frontend chat, daily tasks | Free | Primary |
| Dispatcher | Qwen3-32B (SiliconFlow) | Fallback #1, search tasks | Free | Avoid Gemini rate limit |
| Learner | Doubao Web (Playwright) | Doc summary, archiving | Free | Local port 8100 |
| Architect | Claude Opus 4.6 (mynewapi) | Config changes, decisions | Free | Fallback last resort |

## Fallback Chain Design (9 layers)

```
Sonnet 4.6 (primary)
  -> fail
Qwen3-32B (free dispatcher)
  ->
DeepSeek V3.2 (cheap paid $0.55/M)
  ->
Gemini 3 Pro (free OAuth)
  ->
Llama 70B (Groq free)
  ->
Gemini Flash (free)
  ->
Qwen3-32B (Groq free)
  ->
Kimi K2 Thinking (free)
  ->
Opus 4.6 (last resort)
```

**Cross-platform fault tolerance**: 4 independent platforms (mynewapi / SiliconFlow / Google / Groq), any one fails won't affect others.

## Model Provider Configuration

### 1. mynewapi (Primary)
- API: Anthropic Messages
- Models: Opus 4.6 (fallback) + Sonnet 4.6 (primary)
- Cost: Free quota
- Features: 200K context, Opus supports reasoning

### 2. SiliconFlow (China service)
- API: OpenAI Completions
- Models: DeepSeek V3.2 ($0.55/M) + Qwen3-32B (free) + Kimi K2.5/K2-Thinking
- Features: Fast in China, many free models

### 3. Google Gemini
- API: Google Generative AI + CLI OAuth
- Models: Flash / Pro / Flash Lite
- Cost: Free
- Features: 1M context, multimodal

### 4. Groq (Fast inference)
- API: OpenAI Completions
- Models: Llama 70B + Qwen3-32B
- Cost: Free
- Features: Extremely fast inference

### 5. v1api (Backup)
- API: OpenAI Completions
- Models: DeepSeek V3.2/R1, Grok 4, o4-mini, Sonnet 4.5
- Cost: Paid ($0.28-$4.4/M)
- Features: Multi-model aggregation

### 6. Doubao Web (Local proxy)
- API: OpenAI Completions (local Playwright proxy)
- Port: 8100
- Cost: Free
- Features: Web automation, needs Cookie maintenance

### 7. Volcano Engine Doubao (Official API)
- API: OpenAI Completions
- Models: Doubao 2.0 Pro/Lite
- Cost: Paid ($0.4-$16/M)
- Features: Official API, stable but expensive

## Cron Task Distribution Strategy

### Using Doubao Web (50%)
- Collection scanning (every 2 hours)
- Telegram doc learning (every 2 hours at :30)
- GitHub Trending
- AI community hotspots

### Using Qwen3-32B (50%)
- Management skills learning
- Kitt self-evolution
- OpenViking tracking
- TikTok material mining

**Reason**: Distribute single-point-of-failure risk, Doubao down won't affect overall operation.

## Health Check & Fault Tolerance

### Doubao Health Check (every 30 min)
1. Normal -> Clear fallback flag
2. Abnormal -> Auto restart service (max 3 times)
3. 3 consecutive failures -> Switch to Qwen3 fallback + Telegram notification

### Balance Monitor (daily 22:00)
- Check mynewapi balance
- Below $5 -> Telegram notification to recharge

### Rolling Backup (every 4 hours)
- Config: ~/.openclaw/golden-backup/rolling/
- Memory: Git version control + iCloud sync

## Key Parameters

- Context: 200K tokens
- Compaction: 24K tokens reserved
- Heartbeat: 55 minutes (Gemini Flash)
- Sub-agents: Max 12 concurrent, archive after 60 min
- Memory Search: Local semantic search, 50K cache

## Known Risks & Mitigation

| Risk | Mitigation |
|---|---|
| Doubao Web anti-scraping | Health check + auto restart + Qwen3 fallback |
| mynewapi out of credit | Balance monitor + 9-layer fallback |
| Gemini rate limit | Dispatcher changed to Qwen3, Gemini demoted to #3 |
| Config corruption | Rolling backup + Git version control + iCloud |
| Cookie expiration | Telegram notification + manual re-login |

## Optimization Suggestions Needed

1. **Fallback chain order**: Currently sorted by cost, should it be adjusted by speed or quality?
2. **Cron distribution ratio**: Is 50/50 reasonable? Need dynamic adjustment?
3. **Health check frequency**: Is 30 minutes too frequent?
4. **Balance threshold**: Is $5 appropriate?
5. **Sub-agent model**: Is DeepSeek V3.2 optimal?
6. **Context management**: Is 200K enough? Is compaction strategy reasonable?
7. **Doubao Web architecture**: Need multi-instance deployment (Kimi/ChatGPT/Gemini)?
8. **Cost optimization**: Any cheaper alternatives?

## Attachments
- Redacted config: /tmp/openclaw-redacted.json
- Emergency manual: memory/01_mandatory-rules/emergency-manual.md
- Doubao health check: ~/bin/doubao-healthcheck.py
- Balance monitor: ~/bin/balance-monitor.py
