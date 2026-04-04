import re
import shutil
from pathlib import Path

SRC_DIR = Path('/Users/apple/Desktop/exported-assets')
OUT_DIR = Path('/Users/apple/Desktop/cloud_handoff_perplexity_2026-04-04')
SRC_MD = SRC_DIR / '没完呢.md'
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'images').mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'assets' / 'scripts').mkdir(parents=True, exist_ok=True)

# copy source assets
for p in SRC_DIR.iterdir():
    if p.is_file():
        if p.suffix.lower() == '.png':
            shutil.copy2(p, OUT_DIR / 'images' / p.name)
        elif p.suffix.lower() == '.py':
            shutil.copy2(p, OUT_DIR / 'assets' / 'scripts' / p.name)
        elif p.name == '没完呢.md':
            shutil.copy2(p, OUT_DIR / 'source.md')

text = SRC_MD.read_text(encoding='utf-8', errors='ignore') if SRC_MD.exists() else ''
text = text.replace('\r\n', '\n').replace('\r', '\n')
text = text.replace('***', '\n---\n')
text = re.sub(r'(<img[^>]+>)', r'\n\1\n', text)
text = re.sub(r'(#{1,6}\s)', r'\n\1', text)
text = re.sub(r'\n{3,}', '\n\n', text)

# remove noisy data-uri image payloads / long inline blobs
text = re.sub(r'!\[\]\(data:[^)]+\)', '[embedded image removed from export]', text, flags=re.S)
text = re.sub(r'data:image/[^\s\)]{100,}', '[embedded-image-data]', text, flags=re.S)
text = re.sub(r'\n?\[\.\.\.\s*\d+ more characters truncated\]\n?', '\n', text)

lines = []
for line in text.split('\n'):
    raw = line.strip()
    if not raw:
        lines.append('')
        continue
    if raw == '![](data:':
        lines.append('[embedded image removed from export]')
        continue
    if raw.startswith('data:image/') or len(raw) > 20000:
        lines.append('[large embedded payload removed]')
        continue
    if len(raw) <= 240:
        lines.append(raw)
        continue
    parts = re.split(r'(?<=[。；！？:：])\s*', raw)
    if len(parts) == 1:
        parts = re.split(r'(?<=[\.\!\?])\s+', raw)
    if len(parts) == 1:
        parts = [raw[i:i+220] for i in range(0, len(raw), 220)]
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith('data:image/'):
            lines.append('[embedded image removed from export]')
        else:
            lines.append(p)

clean = '\n'.join(lines)
clean = re.sub(r'\n{3,}', '\n\n', clean).strip() + '\n'
(OUT_DIR / 'source_cleaned.md').write_text(clean, encoding='utf-8')

brief_cn = '''# 接手说明（中文）

## 这个包是什么
这是一个给 Cloud / Claude 接手用的振动刀设备电气设计 handoff 包。
目标不是直接出最终施工图，而是基于现有 markdown、图片、脚本资产，继续整理成可精修的工程草案。

## 当前已有资产
- `source.md`：原始导出 markdown
- `source_cleaned.md`：已做一轮清洗的 markdown
- `images/`：主回路、控制回路、IO、布线、变频器柜、伺服针脚、接地等图片
- `assets/scripts/`：导出残留/辅助脚本，先保留，不假定一定有用
- `spec.md`：目标输出要求
- `claude_working.md`：Claude 后续工作底稿

## 处理边界
1. 不要把现有内容当成最终可施工图。
2. 要区分“已确认事实”和“工程假设”。
3. 不要擅自编造具体器件型号、端子号、线号、PLC 点位。
4. 可以整理、重组、补结构，但不能把缺失数据伪装成已确定。

## Cloud / Claude 下一步重点
1. 先读 `source_cleaned.md`
2. 逐张核对 `images/`
3. 重组为更清晰的工程文档
4. 输出时重点覆盖：
   - power topology
   - main circuit
   - control circuit
   - 24V circuit
   - VFD circuit
   - safety circuit
   - terminal blocks
   - EMI / EMC recommendations
   - missing information

## 当前最可能缺的内容
- 端子号
- 线号
- PLC / 控制卡 IO 对应表
- 伺服/驱动器最终品牌与接口定义
- 变频器联锁细节
- 安全回路细节

## 目标
把当前资产包整理成“可继续精修的电气设计草案”，而不是聊天总结。
'''
(OUT_DIR / 'HANDOFF_ZH.md').write_text(brief_cn, encoding='utf-8')

readme = '''# Claude Handoff Package

## Goal
Take over and refine an industrial electrical design draft captured from exported Perplexity assets.

## Current status
- Source markdown has been imported from local exported assets.
- A cleaned markdown version is available.
- Images and helper scripts have been organized into subfolders.
- This package is meant for refinement, not direct construction use.

## Recommended reading order
1. `HANDOFF_ZH.md`
2. `CLOUD_BRIEF.md`
3. `source_cleaned.md`
4. `images/`
5. `spec.md`
6. `claude_working.md`

## Folder structure
- `source.md` — raw imported markdown
- `source_cleaned.md` — cleaned markdown for first-pass reading
- `HANDOFF_ZH.md` — Chinese handoff context and constraints
- `CLOUD_BRIEF.md` — concise English brief
- `claude_working.md` — Claude's working draft
- `spec.md` — target output requirements
- `images/` — exported diagrams
- `assets/scripts/` — helper or residual python files from export
'''
(OUT_DIR / 'README.md').write_text(readme, encoding='utf-8')

claude = '''# Claude Working Draft

## Imported status
- Source markdown imported from `source.md`
- Cleaned markdown prepared in `source_cleaned.md`
- Images imported into `images/`
- Python helper scripts imported into `assets/scripts/`

## Rules for refinement
- Preserve confirmed facts.
- Separate assumptions from confirmed facts.
- Do not fabricate terminal numbers, wire numbers, IO mappings, or exact device models.
- Use images as cross-checks, not as proof of missing details.

## Next task for Claude
1. Read `HANDOFF_ZH.md`
2. Read `source_cleaned.md`
3. Review all images in `images/`
4. Review helper scripts in `assets/scripts/` only if needed
5. Produce a cleaned and consolidated final deliverable based on `spec.md`
'''
(OUT_DIR / 'claude_working.md').write_text(claude, encoding='utf-8')
