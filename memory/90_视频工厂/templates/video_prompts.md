# 高质量视频提示词模板 v2.0
> 基于 Veo 3.1 官方文档 + VidAU 专业指南 + 碰撞优化

## 核心原则
1. **结构化提示词**：每个参数明确指定，不留模糊空间
2. **前3秒法则**：第一个镜头必须是最震撼的画面
3. **8秒单段**：每段最长8秒，多段拼接
4. **首尾帧控制**：提供参考图片提升连贯性

## 结构公式（8要素）
```
[动作描述] + [镜头运动+速度] + [光线方向+变化] + [景深] +
[节奏] + [风格+参考] + [音效暗示] + [分辨率+时长]
```

## JSON 结构化提示词（高级用法）
```json
{
  "scene": "工厂车间内，CNC切割机正在精密切割皮革",
  "camera": {
    "movement": "slow tracking shot, left to right",
    "angle": "slightly low, looking up at machine",
    "lens": "24mm wide angle",
    "dof": "shallow, focus on cutting head"
  },
  "lighting": {
    "key": "dramatic side light from industrial windows",
    "fill": "ambient factory fluorescent",
    "effect": "volumetric beams through dust particles"
  },
  "style": "industrial documentary, cinematic color grading",
  "mood": "powerful, precise, awe-inspiring",
  "audio": "mechanical hum, precise cutting sounds",
  "duration": "8 seconds",
  "resolution": "1080p"
}
```

## 赛道模板

### 1. 视觉奇观（前3秒：最震撼的全景）
```
[HOOK SHOT] Breathtaking aerial drone shot rapidly descending through clouds,
suddenly revealing a vast [壮观场景] below. Camera continues descending smoothly,
transitioning from bird's eye to eye level. Golden hour sunlight creates long
dramatic shadows across the landscape. Volumetric god rays pierce through scattered
clouds. Slow cinematic pace building to reveal. National Geographic documentary
cinematography. Ambient wind and nature sounds. 8 seconds, 1080p.
photorealistic, cinematic color grading, no text, no watermark.
```

### 2. 知识科普（前3秒：反直觉的视觉）
```
[HOOK SHOT] Extreme macro shot of [微观主体] suddenly pulling back to reveal
the full scale, creating a dramatic sense of perspective shift. Camera smoothly
dollies out while maintaining sharp focus on the subject. Clean, bright lighting
with subtle shadows for depth. Modern educational documentary style with
infographic-like clarity. Gentle electronic ambient music. 8 seconds, 1080p.
hyperrealistic detail, smooth camera movement, no text overlay.
```

### 3. 艺术创意（前3秒：视觉冲击）
```
[HOOK SHOT] A burst of [鲜艳色彩] explodes across the frame, morphing and
transforming into [艺术主体]. Camera slowly orbits as the transformation
continues, revealing intricate details and impossible geometries. Ethereal
lighting shifts from warm amber to cool violet. Dreamlike slow motion with
fluid, organic movement. Experimental art film style. Ambient synthesizer
soundscape. 8 seconds, 1080p. surreal, vibrant, mesmerizing.
```

### 4. 故事叙事（前3秒：悬念/情感钩子）
```
[HOOK SHOT] Close-up of [角色关键细节: 一双手/一个眼神/一个物件],
camera slowly pulls back revealing the full scene and context. Shallow depth
of field with beautiful bokeh. Natural lighting from [光源], creating intimate
atmosphere. Slight handheld camera movement for authenticity. Indie film
aesthetic with warm, slightly desaturated color grading. Soft piano or
acoustic guitar. 8 seconds, 1080p. emotional, cinematic, intimate.
```

### 5. 制造/科技（前3秒：机械之美）
```
[HOOK SHOT] Extreme slow motion of [精密动作: 激光切割/火花飞溅/金属成型],
camera tracks alongside the action at machine speed. Dramatic side lighting
creates stark contrast between bright sparks and dark machine body. Volumetric
light beams through industrial dust and smoke. Camera gradually widens to
reveal the full production line. Industrial documentary cinematography,
shot on RED camera. Mechanical ambient sounds mixed with subtle electronic
score. 8 seconds, 1080p. hyperrealistic, cinematic, powerful.
```

## 多段拼接策略（30秒视频 = 4段）
| 段落 | 时长 | 内容 | 镜头 |
|------|------|------|------|
| 1 | 3秒 | 钩子（最震撼画面） | 特写/航拍/慢动作 |
| 2 | 8秒 | 展开（场景全貌） | 跟踪/环绕 |
| 3 | 8秒 | 高潮（核心内容） | 推进/微距 |
| 4 | 8秒 | 收尾（情感升华） | 拉远/升降 |

## Veo 3.1 避坑指南
- ❌ 不要要求精确文字渲染
- ❌ 不要要求多人复杂互动
- ❌ 不要用模糊描述（"好看的光线"）
- ✅ 用具体镜头术语（"24mm wide angle, f/2.8"）
- ✅ 描述光线方向和变化（"light shifts from warm to cool"）
- ✅ 加 "no text, no watermark" 避免AI水印
- ✅ 加 "photorealistic" 或 "hyperrealistic" 提升真实感
- ✅ 指定 "8 seconds" 获得最长片段
