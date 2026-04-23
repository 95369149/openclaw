#!/bin/bash
# Provider 状态监控脚本 v2
# 使用浏览器抓取客户端渲染的状态页

STATUS_URL="https://status.penguinsaichat.dpdns.org"
OUTPUT_FILE="/Users/apple/.openclaw/workspace/memory/ops/provider-status.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 用 Node.js + Playwright 抓取（如果有）或用 browser tool
# 这里先用简化版：直接调用 openclaw browser

# 临时方案：用之前抓到的数据（今天 13:25 的状态）
# 后续可以改成定期用 browser tool 抓取

cat > "$OUTPUT_FILE" <<'EOF'
{
  "timestamp": "2026-03-10T11:51:30Z",
  "source": "https://status.penguinsaichat.dpdns.org",
  "lastCheck": "manual",
  "providers": {
    "mynewapi": {
      "models": {
        "claude-opus-4-6": {
          "node": "cc7-opus",
          "status": "ok",
          "note": "双节点稳定"
        },
        "claude-sonnet-4-6": {
          "node": "ccmax/ccmax2",
          "status": "ok",
          "note": "双节点稳定"
        }
      }
    },
    "mygptapi": {
      "models": {
        "gpt-5.4": {
          "node": "gpt",
          "status": "degraded",
          "note": "节点异常，建议避免使用"
        }
      }
    },
    "geminiflash": {
      "models": {
        "gemini-3-flash-preview": {
          "node": "gemini",
          "status": "ok"
        }
      }
    },
    "google-gemini-cli": {
      "models": {
        "gemini-3-pro-preview": {
          "node": "local",
          "status": "ok",
          "note": "本地免费"
        }
      }
    }
  },
  "recommendations": {
    "avoid": ["mygptapi/gpt-5.4"],
    "prefer": ["mynewapi/claude-opus-4-6", "mynewapi/claude-sonnet-4-6", "geminiflash/gemini-3-flash-preview"]
  }
}
EOF

echo "✅ Provider status updated (manual snapshot)"
echo "📄 File: $OUTPUT_FILE"
