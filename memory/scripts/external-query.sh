#!/bin/bash
# 外链查询脚本 - 零 token 消耗模式
# 用法: external-query.sh <query> [model]

QUERY="$1"
MODEL="${2:-sonar}"  # 默认用 Perplexity Sonar（免费）
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE="/Users/apple/.openclaw/workspace/memory/shared/external-query_${TIMESTAMP}.md"

echo "🔍 查询: $QUERY"
echo "📡 模型: $MODEL"
echo "📝 输出: $OUTPUT_FILE"
echo ""

# 根据模型选择工具
case $MODEL in
  sonar|perplexity)
    # Perplexity Sonar（免费，不消耗 token）
    echo "使用 Perplexity Sonar..."
    # 这里需要调用 Perplexity API，暂时用占位符
    echo "# 外链查询结果" > "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "**查询**: $QUERY" >> "$OUTPUT_FILE"
    echo "**时间**: $(date)" >> "$OUTPUT_FILE"
    echo "**模型**: Perplexity Sonar" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "（Perplexity API 集成待实现）" >> "$OUTPUT_FILE"
    ;;
  
  doubao)
    # 豆包（免费）
    echo "使用豆包..."
    python3 ~/bin/doubao_client.py "$QUERY" > "$OUTPUT_FILE" 2>&1
    ;;
  
  *)
    echo "❌ 未知模型: $MODEL"
    echo "支持的模型: sonar, perplexity, doubao"
    exit 1
    ;;
esac

echo ""
echo "✅ 查询完成，结果已写入:"
echo "   $OUTPUT_FILE"
echo ""
echo "摘要:"
head -20 "$OUTPUT_FILE"
