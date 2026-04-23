#!/usr/bin/env python3
"""
X Ideas Scanner v2.0 - 五层信息价值链版本
新增：五维评分过滤 + Weaver 跨源关联摘要
"""

import urllib.request
import xml.etree.ElementTree as ET
import time
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net"
]

# 监控账号列表
ACCOUNTS = [
    # AI/Agent 领域
    "OpenAI",
    "AnthropicAI",
    "GoogleAI",
    "sama",
    "karpathy",

    # OpenClaw/AI 工具
    "msjiaozhu",  # MapleShaw
    "starlight1_123",  # 凯迪
    "qingq77",
    "dtdt666",

    # 制造业/CNC（待补充）
    # "cnc_industry",

    # 营销/内容
    "naval",
    "wangray",  # Ray Wang
]

WORKSPACE = Path("/Users/apple/.openclaw/workspace")
IDEAS_FILE = WORKSPACE / "memory" / "ideas.md"
SEEN_FILE = WORKSPACE / "memory" / "ops" / "seen_urls.json"
DIGEST_FILE = WORKSPACE / "memory" / "shared" / f"{datetime.now().strftime('%Y-%m-%d')}_x_digest.md"

# 五维评分阈值（低于此分数丢弃）
SCORE_THRESHOLD = 3.0

# 厂长关注的核心领域（用于相关性评分）
FOCUS_AREAS = [
    "AI Agent", "多模型", "自动化", "工作流",
    "外贸", "出海", "B2B", "制造业",
    "内容创作", "抖音", "公众号",
    "OpenClaw", "LLM", "提示词"
]


def load_seen_urls():
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_urls(urls):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(urls), f, indent=2)


def fetch_rss(username, instance_index=0):
    if instance_index >= len(NITTER_INSTANCES):
        return None
    instance = NITTER_INSTANCES[instance_index]
    url = f"{instance}/{username}/rss"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"❌ {instance} 失败: {e}")
        time.sleep(1)
        return fetch_rss(username, instance_index + 1)


def parse_tweets(xml_data):
    root = ET.fromstring(xml_data)
    tweets = []
    for item in root.findall('.//item'):
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
        desc = item.find('description').text if item.find('description') is not None else ""
        tweets.append({
            'title': title,
            'link': link,
            'pub_date': pub_date,
            'description': desc[:300] if desc else ""
        })
    return tweets


def score_tweet(tweet):
    """
    五维评分（本地轻量版，不调用 LLM 节省成本）
    - Relevance 相关性：命中 FOCUS_AREAS 关键词
    - Novelty 新颖度：含链接/数据/工具名
    - Recency 时效性：默认满分（RSS 本身保证时效）
    - Source 信誉：固定账号列表均为可信源
    - Evidence 证据：含数字/百分比/具体案例
    """
    text = (tweet['title'] + " " + tweet['description']).lower()

    # 相关性（0-2分）
    relevance = min(2, sum(1 for kw in FOCUS_AREAS if kw.lower() in text) * 0.5)

    # 新颖度（0-1分）：含 http/工具名/版本号
    novelty = 1.0 if any(x in text for x in ['http', 'github', 'v2', 'v3', '发布', 'launch', 'new']) else 0.5

    # 时效性（固定1分）
    recency = 1.0

    # 信誉（固定1分，来自白名单账号）
    source = 1.0

    # 证据（0-1分）：含数字
    import re
    evidence = 1.0 if re.search(r'\d+[%xX倍万亿]|\d{4,}', text) else 0.5

    total = relevance + novelty + recency + source + evidence
    return round(total, 2)


def weaver_summary(tweets):
    """
    Weaver 跨源关联：把今日所有高分推文交给 LLM 做信号摘要
    使用 gemini-cli（免费）
    """
    if not tweets:
        return None

    tweet_list = "\n".join([
        f"- @{t['username']} (分数:{t['score']}): {t['title']} {t['link']}"
        for t in tweets
    ])

    prompt = f"""你是一个信息分析师。以下是今天从 X 抓取的高质量推文列表：

{tweet_list}

请完成两件事：
1. **跨源关联**：找出 2-3 个跨账号的共同信号或趋势（不同人在说同一件事）
2. **行动建议**：针对"AI Agent 系统建设"和"外贸拓客"两个场景，各给出 1 条可立即执行的建议

输出格式：
## 今日信号
[跨源关联内容]

## 行动建议
- AI Agent：[建议]
- 外贸拓客：[建议]

控制在 300 字以内。"""

    try:
        result = subprocess.run(
            ['openclaw', 'ask', '--model', 'google-gemini-cli/gemini-3-pro-preview', prompt],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        # fallback: 本地简单摘要
        lines = [f"- @{t['username']} (⭐{t['score']}): {t['title']}" for t in tweets[:10]]
        return "## 今日信号\n" + "\n".join(lines) + "\n\n## 行动建议\n- AI Agent：查看高分推文，提取可落地工具\n- 外贸拓客：关注行业动态，寻找客户信号"
    except Exception as e:
        print(f"⚠️ Weaver 摘要失败: {e}")
        lines = [f"- @{t['username']} (⭐{t['score']}): {t['title']}" for t in tweets[:10]]
        return "## 今日推文列表\n" + "\n".join(lines)
    return None


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始扫描 X 账号 (v2.0 五层过滤)...")

    seen_urls = load_seen_urls()
    new_tweets = []

    for username in ACCOUNTS:
        print(f"📡 抓取 @{username}...", end=" ")

        xml_data = fetch_rss(username)
        if not xml_data:
            print("❌ 所有实例均失败")
            continue

        tweets = parse_tweets(xml_data)
        count = 0

        for tweet in tweets[:5]:
            if tweet['link'] not in seen_urls:
                score = score_tweet(tweet)
                tweet['score'] = score
                tweet['username'] = username

                if score >= SCORE_THRESHOLD:
                    new_tweets.append(tweet)
                    count += 1
                else:
                    print(f"  ⏭️ 低分跳过({score}): {tweet['title'][:40]}")

                seen_urls.add(tweet['link'])

        print(f"✅ {count} 条通过过滤")
        time.sleep(1.5)

    # 写入 ideas.md
    if new_tweets:
        IDEAS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IDEAS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} (v2.0 已过滤)\n\n")
            for t in new_tweets:
                f.write(f"- **@{t['username']}** (⭐{t['score']}): {t['title']}\n")
                f.write(f"  {t['link']}\n\n")

        print(f"\n✅ {len(new_tweets)} 条高质量推文写入 {IDEAS_FILE}")

        # Weaver 跨源关联摘要
        print("🧵 Weaver 生成跨源关联摘要...")
        summary = weaver_summary(new_tweets)
        if summary:
            DIGEST_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DIGEST_FILE, 'w', encoding='utf-8') as f:
                f.write(f"# X 情报日报 {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"抓取账号：{len(ACCOUNTS)} 个 | 通过过滤：{len(new_tweets)} 条\n\n")
                f.write(summary)
                f.write("\n\n---\n\n## 原始推文\n\n")
                for t in new_tweets:
                    f.write(f"- **@{t['username']}** (⭐{t['score']}): {t['title']}\n  {t['link']}\n\n")
            print(f"✅ 摘要写入 {DIGEST_FILE}")
        else:
            print("⚠️ Weaver 摘要跳过（gemini 不可用）")
    else:
        print("\n✅ 无新推文通过过滤")

    save_seen_urls(seen_urls)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 扫描完成")


if __name__ == "__main__":
    main()
