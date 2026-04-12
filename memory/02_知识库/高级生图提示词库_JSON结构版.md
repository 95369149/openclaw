# 高级生图提示词库 (JSON结构版)
> 来源：X (PlayForge AI)
> 核心逻辑：打破1:1常规比例（推荐 4:9 或 9:16），使用具体的物理摄影镜头参数替代堆砌的形容词，采用 JSON 结构精准控制。

## 1. 少女一字马张力感 (比例 4:9)
```json
{ 
  "prompt": "masterpiece, best quality, ultra detailed, 8k, extremely beautiful East Asian teenage girl, celebrity level beauty, perfect oval face, flawless skin, large expressive eyes, delicate features, subtle makeup, long straight black hair tied in neat high bun hairstyle, cute flushed cheeks, embarrassed expression, open mouth slightly, sweat drops on face and neck, dynamic athletic pose, extreme vertical splits against wall, perfect 180 degree high leg raise, one leg straight up vertically pressed against the wall, other leg firmly on floor, one hand gripping the wall for balance, other hand gently holding her own raised leg near the ankle, wearing complete school gym uniform, white short-sleeve gym shirt neatly tucked in, blue sports shorts with white side stripes, full blue tracksuit pants pulled up properly covering legs completely, no skin exposure below waist, innocent dance practice pose, detailed fabric texture, realistic clothing folds and creases, soft natural indoor lighting, school hallway with plain wall background, high resolution, sharp focus, cinematic composition, aspect ratio 4:9", 
  "negative_prompt": "nsfw, nude, naked, exposed, low quality, bad anatomy, deformed, extra limbs, fused fingers, poorly drawn hands, blurry, watermark, text, signature, multiple people, male, boy, man, sexual, erotic, explicit, adult content, cropped legs, distorted proportions, ugly face, mutated hands"
}
```

## 2. 酒吧霓虹主题 (比例 9:16)
```text
An ultra-photorealistic cinematic photograph of a cool 2-year-old Asian muse woman sitting with legs spread in a dark leather booth at a dimly lit bar. She wears red-tinted sunglasses looking upwards, a pink ruched tube top, matching pink pants, a white cardigan, and silver necklaces. She is seductively licking a small stirrer or spoon. The scene is bathed in moody red neon light from a sign reading "Sarty Club" in the background, mixed with warm bokeh lights from the bar crowd. Realistic skin sheen, sweat, and detailed fabric textures. 8K resolution, low-light professional photography. --ar 9:16
```

## 3. 高级影楼 + 午后窗边自然光（经典写真色调）
```json
{
  "subject": {
    "age": 19,
    "gender": "female",
    "ethnicity": "East Asian Thai/Vietnamese mixed blood with approximately 40% Caucasian features",
    "face_shape": "瓜子脸 (sharp V-shaped small delicate face), three庭五眼 perfect ratio",
    "hair_color": "platinum blonde, silky luminous strands",
    "hair_style": "random natural flow, slightly tousled for casual elegance",
    "skin_tone": "extreme cold white porcelain skin, icy jade translucent undertone",
    "skin_quality": "tender ultra-smooth, hydrated dewy, glossy highlight",
    "body_type": "perfect slim athletic figure, elongated slender limbs"
  },
  "expression": {
    "mood": "natural relaxed lazy dreamy serene white-daydream state",
    "emotion": "cute subtle innocent expression, first-love sweetness",
    "eyes": "large clear innocent eyes, natural soft unfocused gaze"
  },
  "clothing": {
    "top": "extremely thin semi-sheer cream/beige long-sleeve top, lightweight chiffon-like fabric",
    "bottom": "high-shine metallic silver mini skirt, mirror-like reflective surface",
    "socks": "thick pale yellow knee-high socks with subtle ribbed texture",
    "style": "form-fitting yet ethereal airy, playful dynamic yet high-end luxurious"
  },
  "pose_and_scene": {
    "pose": "lying relaxed supine on large white linen-draped daybed",
    "location": "luxury high-ceiling photography studio, floor-to-ceiling sheer white curtains",
    "activity": "deeply immersed in reading the poetry book",
    "angle": "slightly high angle casual intimate snapshot"
  },
  "makeup_and_styling": {
    "makeup": "thick glamorous foundation with sheer dewy application, glowy highlight",
    "overall_vibe": "sweet pure idol-like girl, elegant dreamy sophisticated aura"
  },
  "photography_style": {
    "camera": "early 2000s CCD smartphone aesthetic, candid raw snapshot energy",
    "lighting": "strong built-in flash combined with soft directional window natural light",
    "color_tone": "high-end studio portrait color grading, warm-neutral beige dominant (3200-4500K)",
    "grain_noise": "light atmospheric misty fog particles throughout, subtle chromatic noise",
    "focus": "deep selective focus on micro-layers of fabric texture",
    "quality": "32K ultra-high resolution detail, 8K master photographic quality"
  },
  "technical": {
    "aspect_ratio": "9:16",
    "render_style": "hyper photorealistic, highest fidelity cinematic emotion piece"
  }
}
```

## 4. 森林边缘斑驳树影 + 强烈丁达尔效应
> (主体、表情、妆容与上文相同，替换以下部分)
```json
{
  "clothing": {
    "top": "extremely thin semi-sheer sage green to ivory gradient long-sleeve top",
    "bottom": "high-shine soft metallic olive mini skirt",
    "socks": "sheer light khaki knee-highs with faint leaf-like texture",
    "style": "ethereal woodland elegant"
  },
  "pose_and_scene": {
    "pose": "lying relaxed on soft thick moss-covered large flat ancient rock",
    "location": "sun-dappled edge of primeval forest clearing, dense canopy overhead pierced by intense volumetric god rays (strong Tyndall effect)",
    "activity": "serenely immersed in the wildflowers"
  },
  "photography_style": {
    "camera": "early 2000s CCD smartphone aesthetic",
    "lighting": "strong flash fill + dramatic piercing volumetric god rays (intense Tyndall beams)",
    "color_tone": "cool emerald forest green dominant, warm golden sunbeam contrast bursts",
    "aesthetic": ["ethereal dreamy forest haze", "强烈丁达尔效应斑驳树影森林写真"]
  }
}
```

## 5. 海边黄昏金粉光 + 复古胶片
```json
{
  "clothing": {
    "top": "extremely thin semi-sheer off-shoulder cream-to-peach gradient long-sleeve crop top",
    "bottom": "high-shine metallic gold mini skirt with soft pleats",
    "socks": "sheer thin ankle socks in pale gold tint or barefoot"
  },
  "pose_and_scene": {
    "pose": "lying relaxed on large soft white beach towel spread over smooth warm rocks",
    "location": "secluded rocky beach at golden hour sunset",
    "activity": "serenely immersed in the seashell necklace"
  },
  "photography_style": {
    "camera": "early 2000s CCD smartphone aesthetic",
    "lighting": "strong built-in flash fill + rich warm sunset side lighting, intense golden rim light",
    "color_tone": "rich golden-orange highlight dominant, vintage Kodak Portra 400 film emulation",
    "aesthetic": ["黄昏金粉光晕海边高级写真", "vintage film fade adds nostalgic temporal depth"]
  }
}
```

## 其他场景变体 (替换 Clothing 部分)

### 6. 古典花园 + 晨雾柔光
- top: delicate semi-sheer lace-trimmed ivory-to-rose long-sleeve blouse
- bottom: flowy pastel rose midi skirt with soft tulle overlay
- socks: sheer pale mint knee-high stockings with subtle floral embroidery

### 7. 都市loft落地窗 + 冷调霓虹渗入
- top: ultra-thin semi-sheer metallic silver-blue long-sleeve bodysuit top
- bottom: high-shine chrome silver mini skirt with asymmetric hem
- socks: sheer black fishnet knee-highs with subtle sparkle thread

### 8. 雪景木屋窗台 + 冷白高调
- top: extremely thin semi-sheer pure white cashmere-blend long-sleeve top
- bottom: shimmering silver-white mini skirt with faux fur trim
- socks: thick but sheer white knee-high socks with subtle pearl sheen

### 9. 复古图书馆 + 暖灯斑驳
- top: semi-sheer vintage amber-gold long-sleeve blouse
- bottom: high-waist deep caramel mini skirt with soft pleats
- socks: sheer warm taupe knee-highs with lace top

### 10. 沙漠日落沙丘 + 强烈侧逆光
- top: extremely thin semi-sheer emerald-to-gold gradient long-sleeve top
- bottom: shiny metallic green mini skirt with tropical sheen
- socks: sheer pale green knee-highs with subtle leaf motif

### 11. 樱花树下春日散射光 + 粉调梦幻
- top: delicate semi-sheer pale pink-to-white long-sleeve blouse
- bottom: flowy cherry-blossom pink mini skirt with petal-like ruffles
- socks: sheer soft pink knee-highs with subtle lace edge
