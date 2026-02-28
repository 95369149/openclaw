---
name: video-factory
description: >
  谷歌一条龙高质量短视频内容工厂。全流程使用谷歌生态：
  Gemini搜热点 → 生提示词 → Nano Banana生图 → Veo生视频 → ProducerAI配乐 → ffmpeg合成。
  每天产出3条可直接发布抖音/YouTube的高质量短视频。
---

# Video Factory — 谷歌一条龙内容工厂

## 定位
泛内容短视频账号，不绑定特定产品。什么火做什么，追热点+做经典。

## 前置条件
- Gemini Pro 会员（gemini.google.com）
- Google AI Studio 账号（aistudio.google.com）
- ffmpeg 已安装
- OpenClaw browser 工具可用

## 流水线

### Phase 1: 选题（Gemini CLI，免费）

用 main agent（gemini-cli）搜索当日热点，生成3套内容方案。

```bash
# 由 cron 每天 08:00 触发，main agent 执行
# 输出写入 memory/90_视频工厂/YYYY-MM-DD_选题.md
```

选题模板：
```
搜索今日抖音/YouTube热门趋势，从以下5个赛道中各选1个最有潜力的话题：
1. 视觉奇观（震撼场景、自然奇观、城市风光）
2. 知识科普（冷知识、科学解释、生活技巧）
3. 艺术创意（风格转换、创意动画、视觉错觉）
4. 故事叙事（微故事、情感共鸣、悬疑反转）
5. 制造/科技（工厂实拍感、机械之美、科技前沿）

每个话题输出：
- 标题（抖音风格，带钩子）
- 30秒脚本（分镜描述）
- 3个关键帧提示词（Nano Banana用，英文，专业摄影级）
- 1个视频提示词（Veo用，英文，含镜头运动+光线+风格）
- 配乐风格建议
```

### Phase 2: 生图（Nano Banana，AI Studio免费版）

用浏览器操作 aistudio.google.com，选 Nano Banana (gemini-2.5-flash-image)。

提示词质量标准（必须包含）：
```
[主体描述], [场景环境], [光线方向: golden hour/dramatic side lighting/soft diffused],
[镜头类型: close-up/wide angle/aerial/macro], [风格: cinematic/documentary/editorial],
[画质: 4K, sharp focus, high detail], [色调: warm/cool/moody/vibrant]
```

示例（高质量提示词）：
```
A massive CNC laser cutting machine slicing through thick steel plate,
sparks flying in slow motion, dramatic side lighting from factory windows,
wide angle shot, industrial documentary style, 4K ultra sharp,
warm orange tones contrasting with cool blue steel, smoke particles visible in light beams
```

每个选题生成3张关键帧，选最好的1-2张进入视频环节。

### Phase 3: 生视频（Veo 3.1，Gemini Pro会员）

用浏览器操作 gemini.google.com，点"创作视频"。

视频提示词质量标准：
```
[动作描述], [镜头运动: slowly orbiting/tracking shot/dolly zoom/crane shot],
[光线变化: light shifts from warm to cool], [节奏: slow and cinematic/fast-paced],
[音效暗示: mechanical sounds/ambient music], [时长: 8 seconds],
[风格: cinematic/documentary/commercial], [分辨率: 1080p]
```

示例：
```
Cinematic tracking shot of a precision cutting machine in action,
camera slowly moves from left to right revealing the full production line,
dramatic industrial lighting with volumetric light beams through dust particles,
shallow depth of field focusing on the cutting head,
slow motion sparks, documentary style, 1080p, warm color grading
```

每天最多3个视频（Pro会员额度）。

### Phase 4: 配乐（ProducerAI / gemini.google.com）

在 gemini.google.com 点"🎸创作音乐"。

配乐提示词模板：
```
[情绪: epic/inspiring/mysterious/energetic],
[风格: cinematic orchestral/electronic/lo-fi/ambient],
[节奏: 120bpm/slow build/steady pulse],
[乐器: strings/synth/piano/percussion],
[时长: 30 seconds],
[用途: background music for short video]
```

### Phase 5: 合成（ffmpeg，本地）

```bash
# 基础合成命令
ffmpeg -i video.mp4 -i music.mp3 \
  -filter_complex "[1:a]volume=0.3[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:v copy -shortest output.mp4

# 加字幕（ASS格式）
ffmpeg -i output.mp4 -vf "ass=subtitle.ass" -c:a copy final.mp4

# 加片头（3秒）
ffmpeg -i intro.mp4 -i output.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1" final.mp4

# 竖屏适配（抖音 9:16）
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:a copy vertical.mp4
```

### Phase 6: TTS旁白（可选，Gemini TTS）

在 AI Studio 选 Text to Speech，生成中文/英文旁白。

## TikTok/抖音算法优化（2026）

### 核心机制
- 新视频先推给小群体测试，表现好才扩散
- 80%完播率 = 显著推荐加成
- 零粉丝也能爆（基于内容发现，不是粉丝数）

### 爆款公式
1. **前3秒法则**：第一帧必须是最震撼的画面，决定用户是否继续看
2. **15-30秒黄金长度**：短视频更容易高完播率
3. **无脸内容（Faceless）**：旁白+字幕+AI画面，命中算法最高权重信号
4. **情感注入**：纯AI画面+人声旁白，增加"人味"（TikTok 2026强调 Irreplaceable Instinct）
5. **热门音效**：使用平台热门音乐/音效，算法加权

### 双版本输出
- 抖音版：9:16竖屏 + 中文字幕 + 中文旁白
- YouTube版：16:9横屏 + 英文字幕 + 英文旁白

## 质量检查清单

每条视频发布前必须过：
- [ ] 前3秒有视觉冲击（钩子）
- [ ] 视频长度 15-30秒
- [ ] 画面清晰度 ≥ 1080p
- [ ] 无明显AI痕迹（手指、文字、面部变形）
- [ ] 配乐与画面节奏匹配
- [ ] 字幕无错别字，时间轴同步
- [ ] 标题有钩子（疑问/数字/反转）
- [ ] 有旁白或热门音效（增加"人味"）
- [ ] 竖屏版和横屏版都已导出

## 输出目录

```
memory/90_视频工厂/
├── YYYY-MM-DD_选题.md          # 每日选题方案
├── YYYY-MM-DD_生产日志.md      # 生产过程记录
├── assets/                     # 素材文件
│   ├── images/                 # 关键帧图片
│   ├── videos/                 # 原始视频
│   ├── music/                  # 配乐
│   └── final/                  # 成品视频
└── templates/                  # 提示词模板库
    ├── image_prompts.md        # 图片提示词模板
    ├── video_prompts.md        # 视频提示词模板
    └── music_prompts.md        # 配乐提示词模板
```

## Cron 调度

| 任务 | 时间 | Agent | 内容 |
|------|------|-------|------|
| 选题 | 每天 08:00 | main（gemini-cli） | 搜热点+生成3套方案 |
| 生产 | 每天 10:00 | jimmy（浏览器） | 执行生图+生视频+配乐 |
| 合成 | 每天 14:00 | jimmy（ffmpeg） | 合成+质检+导出 |

## 提示词进化

每周回顾：
- 哪些提示词产出的内容质量最高？
- 哪些赛道的播放量最好？
- 收集爆款视频的提示词，加入模板库
- 参考 memory/80_收藏/2026-02-28_Nano-Seedance提示词合集.md 中的资源
