# 高清肤质与人像质感增强提示词库 (2026版)

> 本套提示词专门用于：保构图、保色调、提清晰度、强化皮肤/发丝/布料细节的高质感修图。
> 适用模型：Nano Banana 2 / Kling 3.0 / Midjourney / Stable Diffusion。

## 核心理念
这不是“换脸”或“换风格”提示词，而是将普通图片提升至 **“高端美妆摄影棚质感”** 的后处理指令。重点针对：毛孔、纹理、光影过渡、边缘锐度。

---

## 1. 中文版 (适用 Nano Banana 2 / 豆包 / 国内模型)

**标准版（直接复制）：**
> 在保持原图精确构图和整体色彩不变的前提下，极大提升图像分辨率与画质。去除所有模糊感，使人物肌肤呈现逼真且细腻的质感：清晰可见的毛孔、细腻的微小纹路，以及自然柔和的光影过渡。保留原图的浅色调和背景氛围，同时重点优化眼部、睫毛、嘴唇细节，并提升发丝与衣物边缘的锐度。最终呈现出拥有高端美妆商业摄影般的质感，肤质真实、自然、不做作。

**微调指南：**
- 如果想要更水润：加入 `“增强皮肤的水光感与高光表现”`
- 如果想要电影感：加入 `“增加环境光的对比度，呈现电影级质感”`

---

## 2. 英文版 (适用 Midjourney / SD / Kling / 国外模型)

**Standard Version (Copy & Paste):**
> Enhance and upscale the image quality while strictly maintaining the original composition and color grading. Remove all blurriness to reveal a highly realistic and detailed skin texture: clear pores, fine natural micro-textures, and smooth lighting transitions. Preserve the original light tones and background atmosphere. Greatly sharpen and optimize the details around the eyes, eyelashes, lips, and individual hair strands. The final output should have the aesthetic of high-end commercial beauty photography, featuring natural, unretouched-looking flawless skin. --v 6.0 --style raw

**Keywords to add for specific effects:**
- **For freckles/imperfections:** `subtle natural freckles, realistic skin imperfections`
- **For lighting:** `studio lighting, soft softbox light, Rembrandt lighting`
- **For macro details:** `macro photography, 85mm lens, extreme close-up details`

---

## 3. 工作流建议

如果你想把一张普通网图做成这种效果：
1. **输入原图** 作为垫图 (Image Prompt / Image to Image)
2. **设置权重**：如果你希望原图变形少，将 Image Weight (iw) 调高（如 Midjourney 中的 `--iw 1.5`）
3. **输入上述提示词**
4. 如果是用 Kling 等视频工具，可用上述生成的 4K 图片作为起幅图片，生成微动态视频。
