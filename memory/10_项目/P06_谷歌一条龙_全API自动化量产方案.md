# P06: 谷歌生态短视频全 API 自动化量产方案

> 最后更新: 2026-03-01
> 状态: 方案设计完成，待落地
> 负责人: Kitt 系统

---

## 一、战略定位

**一句话**：用 Google 全家桶 API 实现"选题→脚本→关键帧→视频→配乐→成片"六步无人值守量产，每天稳定产出 3 条可直接发布的短视频。

**为什么选谷歌生态**：
- Gemini 3 Pro 做编导大脑（免费 OAuth 额度，超强推理）
- Imagen 4 Fast 生图 $0.02/张（全网最低）
- Veo 3 生视频 $0.15/秒（Fast）或 $0.40/秒（Core）
- Lyria 3 配乐（Gemini App 内测中，API 走 Lyria 2 过渡）
- 全链路一个 GCP 账号搞定，不用拼凑多家 API

**双轨并行**：
| 轨道 | 定位 | 内容 | 发布渠道 |
|------|------|------|----------|
| A轨-HTYCNC | 产品营销 | 切割机展示、客户案例、技术科普 | TikTok + YouTube |
| B轨-泛内容 | 流量矩阵 | 热点追踪、视觉奇观、知识科普 | 抖音 + YouTube Shorts |

---

## 二、成本核算（每条视频）

### 单条 30 秒短视频成本

| 环节 | 工具 | 调用量 | 单价 | 小计 |
|------|------|--------|------|------|
| 选题+脚本 | Gemini 3 Pro (OAuth) | ~2000 tokens | 免费 | $0.00 |
| 关键帧 | Imagen 4 Fast | 6 张（含备选） | $0.02/张 | $0.12 |
| 视频片段 | Veo 3 Fast | 30 秒（5×6s） | $0.15/秒 | $4.50 |
| 配乐 | Lyria 2 API / 免费音乐库 | 1 首 30s | ~$0.10 | $0.10 |
| 字幕+合成 | FFmpeg 本地 | — | 免费 | $0.00 |
| **合计** | | | | **$4.72** |

### 月度预算（每天 3 条）

| 方案 | 日产量 | 月产量 | 月成本 | 备注 |
|------|--------|--------|--------|------|
| 经济版 | 3 条 | 90 条 | ~$425 | 全用 Veo 3 Fast |
| 品质版 | 3 条 | 90 条 | ~$1,125 | 关键镜头用 Veo 3 Core |
| 混合版（推荐） | 3 条 | 90 条 | ~$650 | 首尾镜头 Core，中间 Fast |

**对比人工成本**：一个视频剪辑师月薪 8000-15000 元，且产能上限约 30 条/月。AI 量产 90 条/月成本约 4700 元（混合版），且 24 小时不停。

---

## 三、技术架构

### 3.1 API 接入方式

```
┌─────────────────────────────────────────────────┐
│                  调度中枢 (jimmy)                 │
│         cron 每天 08:00 / 14:00 / 20:00          │
└──────────┬──────────────────────────┬────────────┘
           │                          │
    ┌──────▼──────┐           ┌──────▼──────┐
    │  A轨-HTYCNC  │           │  B轨-泛内容  │
    └──────┬──────┘           └──────┬──────┘
           │                          │
           ▼                          ▼
┌─────────────────────────────────────────────────┐
│              Pipeline 执行引擎 (Python)            │
│                                                   │
│  Step 1: Gemini 3 Pro → 选题+脚本+Prompt生成       │
│          ↓                                        │
│  Step 2: Imagen 4 Fast API → 关键帧图片 (并发)      │
│          ↓                                        │
│  Step 3: Veo 3 API → 视频片段 (Image-to-Video)     │
│          ↓                                        │
│  Step 4: Lyria 2 API → BGM 生成                    │
│          ↓                                        │
│  Step 5: FFmpeg → 拼接+字幕+压制                    │
│          ↓                                        │
│  Step 6: 审核推送 → Telegram 确认 → 发布            │
└─────────────────────────────────────────────────┘
```

### 3.2 各环节 API 详情

#### Step 1: 编导大脑 — Gemini 3 Pro

- **接入**：Google AI Studio API Key 或 OAuth（google-gemini-cli）
- **模型**：`gemini-3-pro-preview`
- **成本**：OAuth 免费额度足够，API Key 也极低
- **输入**：热点数据 + 内容矩阵模板 + 品牌调性库
- **输出**：JSON 格式的完整生产包

```python
# 输出结构
{
  "title": "一刀切开10层皮革，这台机器太猛了",
  "hook": "你见过一刀切开10层皮革的机器吗？",
  "scenes": [
    {
      "id": 1,
      "duration": 6,
      "description": "机器全景，红色机身，工厂环境",
      "imagen_prompt": "Wide angle shot of a large red HTYCNC CNC cutting machine in a modern factory, dramatic side lighting from tall windows, industrial documentary style, 4K ultra sharp, warm orange tones, clean concrete floor, organized workspace",
      "veo_prompt": "Slow dolly-in shot revealing a massive red CNC cutting machine in a modern factory, camera moves from wide to medium shot, dramatic side lighting shifts as camera moves, ambient factory sounds, industrial documentary style, 6 seconds, 1080p",
      "veo_model": "fast"
    },
    {
      "id": 2,
      "duration": 6,
      "description": "刀头特写，切割皮革瞬间",
      "imagen_prompt": "Extreme close-up macro shot of an oscillating blade cutting through multiple layers of genuine leather, sparks and leather particles visible, shallow depth of field, dramatic backlight, 4K ultra sharp detail, warm amber tones",
      "veo_prompt": "Macro close-up of oscillating blade slicing through 10 layers of stacked leather, slow motion, leather fibers separating cleanly, particles floating in backlit air, satisfying cutting sound, 6 seconds, 1080p",
      "veo_model": "core"
    }
  ],
  "music_prompt": "Powerful industrial electronic beat, building tension, 120 BPM, cinematic bass drops, metallic percussion elements",
  "subtitles": [...],
  "hashtags": ["#CNC", "#cutting", "#manufacturing", "#leather"]
}
```

#### Step 2: 关键帧生成 — Imagen 4 Fast

- **接入**：Vertex AI API 或 Google AI Studio API
- **模型**：`imagen-4-fast`（$0.02/张）
- **备选**：`imagen-4-standard`（$0.04/张，复杂场景用）
- **并发**：支持批量并发请求，6 张图 < 10 秒

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

# 生成关键帧
response = client.models.generate_images(
    model="imagen-4-fast",
    prompt=scene["imagen_prompt"],
    config=genai.types.GenerateImagesConfig(
        number_of_images=2,        # 每个分镜生成2张备选
        aspect_ratio="16:9",       # 横屏
        output_mime_type="image/png"
    )
)

# 保存图片
for i, img in enumerate(response.generated_images):
    img.image.save(f"scene_{scene['id']}_{i}.png")
```

#### Step 3: 视频生成 — Veo 3

- **接入**：Gemini API 或 Vertex AI
- **模型**：`veo-3.0-generate-preview`（Fast）/ `veo-3.0-generate`（Core）
- **能力**：
  - Text-to-Video：纯文字生成
  - Image-to-Video：关键帧 → 视频（推荐，画面一致性更好）
  - 分辨率：720p / 1080p / 4K
  - 时长：4s / 6s / 8s 单段
  - 原生音效：Veo 3 自带同步音效和对话
  - 续拍：可链式续拍，最长 148 秒
- **关键参数**：
  - `reference_images`：最多 3 张参考图（控制风格一致性）
  - `first_frame` / `last_frame`：精确控制起止画面
  - `enhance_prompt`：自动优化提示词

```python
from google import genai
from google.genai import types
import base64

client = genai.Client(api_key="YOUR_API_KEY")

# Image-to-Video: 关键帧驱动
with open("scene_1_0.png", "rb") as f:
    image_bytes = f.read()

response = client.models.generate_videos(
    model="veo-3.0-generate-preview",  # Fast 版本
    prompt=scene["veo_prompt"],
    image=types.Image(
        image_bytes=image_bytes,
        mime_type="image/png"
    ),
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        duration_seconds=6,
        resolution="1080p",
        enhance_prompt=True,
        include_audio=True       # Veo 3 原生音效
    )
)

# 异步轮询结果
operation = response
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

# 下载视频
for video in operation.result.generated_videos:
    video.video.save(f"scene_{scene['id']}.mp4")
```

#### Step 4: 配乐 — Lyria 2 API（过渡方案）+ Lyria 3（目标方案）

**当前状态**（2026.03）：
- Lyria 3：仅 Gemini App 内测，无公开 API
- Lyria 2 API：Vertex AI 可用（`lyria-002`），纯器乐，30 秒
- Lyria RealTime API：WebSocket 实时生成，适合交互场景

**过渡方案**（推荐）：
```python
# 方案 A: Lyria 2 API 生成器乐 BGM
response = client.models.generate_music(
    model="lyria-002",
    prompt=production_pack["music_prompt"],
    config=types.GenerateMusicConfig(
        duration_seconds=30
    )
)

# 方案 B: 使用 Veo 3 原生音效 + 免费版权音乐库补充
# Veo 3 生成的视频自带环境音效和机械声
# 只需叠加一层 BGM，可用 Pixabay/Uppbeat 免费音乐
```

**目标方案**（Lyria 3 API 开放后）：
- 支持文字/图片/视频作为参考生成音乐
- 支持人声和歌词
- 30 秒完整曲目

#### Step 5: 合成 — FFmpeg 本地处理

```bash
#!/bin/bash
# 拼接视频片段
ffmpeg -f concat -safe 0 -i scenes.txt -c copy merged.mp4

# 叠加 BGM（Veo 原生音效保留，BGM 降低音量混合）
ffmpeg -i merged.mp4 -i bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[va];[1:a]volume=0.3[ba];[va][ba]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy with_bgm.mp4

# 添加硬字幕（SRT 由 Gemini 生成）
ffmpeg -i with_bgm.mp4 -vf "subtitles=subs.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Bold=1'" \
  -c:a copy subtitled.mp4

# 压制双版本
# 竖屏 9:16 (TikTok/Shorts)
ffmpeg -i subtitled.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy output_vertical.mp4
# 横屏 16:9 (YouTube)
ffmpeg -i subtitled.mp4 -vf "scale=1920:1080" -c:a copy output_horizontal.mp4
```

#### Step 6: 审核与发布

```
Pipeline 完成 → 成片推送到 Telegram
  → 厂长预览（视频+脚本+成本明细）
  → 点击 [✅ 发布] → 自动上传 TikTok/YouTube
  → 点击 [🔄 重做] → 指定环节重新生成
  → 点击 [❌ 废弃] → 记录原因，优化提示词库
```

---

## 四、质量控制体系

### 4.1 提示词工程（核心竞争力）

**分层提示词库**：
```
memory/90_视频工厂/
├── prompts/
│   ├── brand_identity.md      # 红太阳品牌视觉标准
│   ├── camera_language.md     # 镜头语言库（50+ 运镜描述）
│   ├── lighting_library.md    # 光线描述库（30+ 光效）
│   ├── style_presets.md       # 风格预设（工业/科技/温暖/震撼）
│   └── negative_prompts.md   # 负面提示词（避免的画面）
├── templates/
│   ├── htycnc_product.json    # A轨产品展示模板
│   ├── htycnc_case.json       # A轨客户案例模板
│   ├── trending_visual.json   # B轨视觉奇观模板
│   └── knowledge_explainer.json # B轨知识科普模板
└── quality/
    ├── checklist.md           # 质量检查清单
    └── feedback_log.md        # 反馈记录（持续优化）
```

**品牌视觉标准**（写入每个 Imagen/Veo prompt 的 System 前缀）：
```
Brand: HTYCNC (红太阳数控)
Colors: Primary red (#CC0000), industrial gray, warm amber accents
Environment: Modern clean factory, organized workspace, professional lighting
Mood: Powerful, precise, trustworthy, innovative
Camera: Cinematic, documentary-grade, steady movements
Quality: 4K sharp, high dynamic range, professional color grading
NEVER: Messy workspace, poor lighting, blurry, cartoon style, anime
```

### 4.2 自动质量检测

在 Veo 生成后、合成前，用 Gemini Vision 自动审查：

```python
# 质量检测 prompt
quality_check_prompt = """
审查这段 AI 生成的视频截帧，检查以下问题：
1. 物理变形（手指数量、物体扭曲、不自然运动）
2. 画面一致性（前后帧风格/颜色是否统一）
3. 品牌合规（是否符合工业/专业调性）
4. 文字清晰度（如有文字是否可读）

输出 JSON: {"pass": true/false, "issues": [...], "score": 0-100}
分数 < 70 自动触发重新生成。
"""
```

### 4.3 A/B 测试机制

- 每个选题生成 2 个版本（不同开头钩子）
- 先发 A 版本，24 小时后看数据
- 数据好的风格写入提示词库，差的写入负面清单
- 每周自动汇总 → 优化模板

---

## 五、落地路线图

### Phase 0: 基建准备（1-2 天）

| 任务 | 负责 | 产出 |
|------|------|------|
| GCP 项目开通 Vertex AI | 厂长 | 项目 ID + Service Account JSON |
| Google AI Studio API Key | 厂长 | API Key（Imagen 4 + Veo 3） |
| 验证 Imagen 4 Fast API 可调通 | deep | 测试脚本 + 样图 |
| 验证 Veo 3 Fast API 可调通 | deep | 测试脚本 + 样片 |
| 验证 Lyria 2 API 或备选方案 | deep | 测试脚本 + 样音 |

### Phase 1: MVP 跑通（3-5 天）

| 任务 | 负责 | 产出 |
|------|------|------|
| 编写 `video_pipeline.py` 核心引擎 | deep | 可执行的 Python 脚本 |
| 建立提示词库（品牌+镜头+光线） | jimmy | memory/90_视频工厂/prompts/ |
| 手动触发跑通 1 条完整视频 | jimmy | 第一条成片 + 成本报告 |
| 质量评估 + 提示词调优 | 厂长 | 反馈 → 优化 |

### Phase 2: 自动化（3-5 天）

| 任务 | 负责 | 产出 |
|------|------|------|
| Cron 定时触发（08:00/14:00/20:00） | jimmy | cron 配置 |
| Telegram 审核推送 + 按钮交互 | jimmy | 审核流程 |
| 错误重试 + 降级策略 | deep | 容错逻辑 |
| 成本监控仪表盘 | deep | 日/周/月成本统计 |

### Phase 3: 规模化（持续优化）

| 任务 | 负责 | 产出 |
|------|------|------|
| A/B 测试自动化 | deep | 数据驱动优化 |
| Lyria 3 API 接入（开放后） | deep | 音乐生成升级 |
| 自动发布到 TikTok/YouTube | deep | 发布脚本 |
| 多账号矩阵管理 | jimmy | 账号调度系统 |

---

## 六、风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| Veo 3 API 限流 | 高 | 日产量受限 | 错峰调用 + 预生成缓冲池 |
| 生成质量不稳定 | 中 | 废片率高 | 自动质检 + 多次重试 + 人工审核 |
| Lyria 3 API 迟迟不开放 | 中 | 配乐环节受限 | Lyria 2 + 免费音乐库过渡 |
| Google 调价 | 低 | 成本上升 | 监控价格变动 + 备选方案（Kling/Seedance） |
| 内容同质化 | 中 | 流量下降 | 多模板轮换 + 热点追踪 + 风格变化 |
| API Key 额度耗尽 | 低 | 停产 | 多 Key 轮换 + 用量告警 |

---

## 七、与现有 Skill 的关系

| Skill | 定位 | 与 P06 关系 |
|-------|------|------------|
| video-factory | 浏览器手动操作版 | P06 是其 API 自动化升级版，替代关系 |
| video-content | 纯脚本生成（无图/视频） | P06 的 Step 1 吸收其内容矩阵和脚本公式 |
| x-reader | 舆情抓取 | 为 B轨选题提供热点数据源 |

**最终目标**：P06 落地后，video-factory 升级为全 API 版本，video-content 的脚本模板并入 P06 的模板库。

---

## 八、第一步行动

**厂长需要做的**：
1. 确认 GCP 项目是否已开通 Vertex AI（或用 Google AI Studio API Key 也行）
2. 确认月度预算上限（建议先按混合版 $650/月 = ¥4700/月 试跑）
3. 确认优先做 A轨（HTYCNC 产品）还是 B轨（泛内容）还是双轨并行

**我立即可以做的**：
1. 用现有 Google AI Studio API Key 测试 Imagen 4 Fast 和 Veo 3 API 是否可调通
2. 建立提示词库初版
3. 编写 pipeline 核心代码骨架
