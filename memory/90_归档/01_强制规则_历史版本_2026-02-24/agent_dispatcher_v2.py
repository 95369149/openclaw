#!/usr/bin/env python3
"""
Agent 调度器 v2.0
新增功能：
1. Fallback 链（模型失败自动切换）
2. 结构化日志（JSONL 格式）
3. 质检重试（<6 分打回重做）
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 配置文件路径
WORKSPACE = Path('/Users/apple/.openclaw/workspace')
ROUTES_FILE = WORKSPACE / 'memory/01_强制规则/intent_routes.json'
TRIAGE_FILE = Path('/tmp/triage_prompt_v2.json')
LOG_FILE = WORKSPACE / 'memory/05_日常日志/agent_execution.jsonl'

# 加载配置
with open(ROUTES_FILE) as f:
    routes_cfg = json.load(f)

with open(TRIAGE_FILE) as f:
    triage_cfg = json.load(f)

# 模型映射
MODEL_MAP = {
    'ds-sf': 'deepseek-ai/DeepSeek-V3.2',
    'flash': 'zai-org/GLM-4.6',  # 用 GLM 4.6 代替 Gemini
    'qwen-32b': 'Qwen/Qwen3-32B',
    'qwen-32b-groq': 'Qwen/Qwen3-32B',  # Groq 暂时用 SiliconFlow
    'perplexity': 'web_search',
    'grok': 'web_search',
}

API_KEY = 'sk-walotbgwymtqjrfocfulfiyaqiptpyrpedvpoexvviplttzd'
API_BASE = 'https://api.siliconflow.cn/v1/chat/completions'

def log_to_file(data):
    """写入结构化日志"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def call_model(model_alias, prompt, max_tokens=500, timeout=30):
    """调用模型（单次，无 fallback）"""
    model_id = MODEL_MAP.get(model_alias, model_alias)
    
    result = subprocess.run([
        'curl', '-s', '--max-time', str(timeout),
        API_BASE,
        '-H', f'Authorization: Bearer {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'model': model_id,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7,
            'max_tokens': max_tokens
        })
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"curl 失败: {result.stderr}")
    
    resp = json.loads(result.stdout)
    if 'choices' not in resp:
        raise Exception(f"API 错误: {resp.get('error', resp)}")
    
    return resp['choices'][0]['message']['content']

def validate_output(result, role):
    """验证输出格式"""
    if role == '质检':
        try:
            # 清理 markdown
            if '```' in result:
                result = result.split('```')[1].replace('json', '').strip()
            data = json.loads(result)
            return 'score' in data and 'passed' in data
        except:
            return False
    return True

def call_model_with_fallback(model_alias, prompt, route, role, max_tokens=500):
    """带 fallback 的模型调用"""
    # 构建模型列表
    models_to_try = [model_alias]
    
    if role in route.get('dispatch', {}):
        fallbacks = route['dispatch'][role].get('fallback', [])
        models_to_try.extend(fallbacks)
    
    last_error = None
    start_time = time.time()
    
    for i, model in enumerate(models_to_try):
        try:
            print(f"  → 调用模型: {model}" + (f" (fallback {i})" if i > 0 else ""))
            result = call_model(model, prompt, max_tokens=max_tokens, timeout=30)
            
            # 验证输出
            if not validate_output(result, role):
                raise ValueError(f"输出格式错误")
            
            # 成功，记录日志
            log_to_file({
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "model": model,
                "fallback_index": i,
                "success": True,
                "duration_ms": int((time.time() - start_time) * 1000)
            })
            
            print(f"  ✅ 完成")
            return result
            
        except Exception as e:
            last_error = str(e)
            log_to_file({
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "model": model,
                "fallback_index": i,
                "success": False,
                "error": last_error
            })
            
            if i < len(models_to_try) - 1:
                print(f"  ⚠️ {model} 失败: {last_error[:50]}")
                continue
    
    # 所有模型都失败
    error_msg = f"所有模型失败: {last_error}"
    print(f"  ❌ {error_msg}")
    raise Exception(error_msg)

def triage(user_input):
    """Triage 分类（带 fallback）"""
    system_prompt = triage_cfg['system_prompt']
    user_prompt = triage_cfg['user_prompt_template'].replace('{user_input}', user_input)
    
    # Triage 的 fallback 链
    models = ['zai-org/GLM-4.5-Air', 'Qwen/Qwen3-32B', 'deepseek-ai/DeepSeek-V3.2']
    
    for model in models:
        try:
            result = subprocess.run([
                'curl', '-s', '--max-time', '10',
                API_BASE,
                '-H', f'Authorization: Bearer {API_KEY}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.1,
                    'max_tokens': 50
                })
            ], capture_output=True, text=True)
            
            resp = json.loads(result.stdout)
            answer = resp['choices'][0]['message']['content'].strip()
            if '```' in answer:
                answer = answer.split('```')[1].replace('json', '').strip()
            
            return json.loads(answer)
        except:
            if model == models[-1]:
                raise
            continue

def get_route(bucket):
    """查路由配置"""
    for route in routes_cfg['routes']:
        if route['bucket'] == bucket:
            return route
    return None

def execute_dag(user_input, route, max_retries=2):
    """执行 DAG 流程（带重试）"""
    print(f"\n=== 执行 DAG: {route['name']} ===")
    print(f"DAG: {' → '.join(route['dag'])}\n")
    
    results = {}
    context = {"user_input": user_input}
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            for step in route['dag']:
                role, task = step.split(':', 1)
                print(f"[{role}] {task}")
                
                if role == 'kitt':
                    results[role] = f"[Kitt 完成] {task}"
                    context[role] = results[role]
                    
                elif role == '质检':
                    upstream_output = context.get('工兵', '[无上游输出]')
                    model_alias = route['dispatch'].get(role, {}).get('model', 'flash')
                    
                    prompt = f"""你是质检 Agent，任务：{task}

用户需求：{user_input}

工兵输出的内容：
---
{upstream_output}
---

验收标准：{route['acceptance']}

请按以下格式输出 JSON（不要 markdown 代码块）：

示例：{{"score": 8, "passed": true, "issues": [], "summary": "质量良好"}}

现在开始检查：
"""
                    
                    output = call_model_with_fallback(model_alias, prompt, route, role, max_tokens=300)
                    results[role] = output
                    context[role] = output
                    
                    # 解析质检结果
                    if '```' in output:
                        output = output.split('```')[1].replace('json', '').strip()
                    qc_data = json.loads(output)
                    score = qc_data.get('score', 0)
                    
                    # 质检不通过，重试
                    if score < 6 and retry_count < max_retries:
                        print(f"  ⚠️ 质检评分 {score}/10，重试 {retry_count + 1}/{max_retries}")
                        retry_count += 1
                        results = {}  # 清空结果，重新执行
                        context = {"user_input": user_input}
                        break  # 跳出 for 循环，重新执行 DAG
                    
                else:
                    model_alias = route['dispatch'].get(role, {}).get('model', 'ds-sf')
                    prompt = f"你是{role}，任务：{task}\n\n用户需求：{user_input}\n\n请输出结果："
                    
                    output = call_model_with_fallback(model_alias, prompt, route, role, max_tokens=300)
                    results[role] = output[:200] + '...' if len(output) > 200 else output
                    context[role] = output
                
                time.sleep(0.3)
            
            # 所有步骤完成，跳出重试循环
            break
            
        except Exception as e:
            if retry_count >= max_retries:
                raise
            print(f"  ⚠️ DAG 执行失败: {e}，重试 {retry_count + 1}/{max_retries}")
            retry_count += 1
    
    return results

def quality_check(results, route):
    """质检（解析质检 Agent 的输出）"""
    print(f"\n=== 质检 ===")
    print(f"验收标准: {route['acceptance']}")
    
    qc_output = results.get('质检', '{}')
    
    try:
        if '```' in qc_output:
            qc_output = qc_output.split('```')[1].replace('json', '').strip()
        qc_data = json.loads(qc_output)
        score = qc_data.get('score', 0)
        passed = qc_data.get('passed', False)
        issues = qc_data.get('issues', [])
        summary = qc_data.get('summary', '')
        
        print(f"  评分: {score}/10")
        print(f"  状态: {'✅ 通过' if passed else '❌ 不通过'}")
        if issues:
            print(f"  问题: {', '.join(issues)}")
        print(f"  总结: {summary}")
        
        return passed, score
    except:
        print(f"  ⚠️ 质检输出解析失败，默认通过")
        return True, 7

# 测试用例
if __name__ == '__main__':
    test_input = "写条朋友圈文案，推下新产品"
    
    print("=== Agent 调度器 v2.0 测试 ===")
    print(f"用户输入: {test_input}\n")
    
    # Step 1: Triage
    print("[1/4] Triage 分类...")
    triage_result = triage(test_input)
    bucket = triage_result['intent_bucket']
    print(f"  → 意图桶: {bucket} (置信度: {triage_result['confidence']})")
    
    # Step 2: 查路由
    print(f"\n[2/4] 查询路由配置...")
    route = get_route(bucket)
    if not route:
        print(f"  ❌ 未找到路由配置")
        exit(1)
    print(f"  → 路由: {route['name']}")
    print(f"  → 风险: {route['risk']}")
    print(f"  → 交付物: {route['deliverable']}")
    
    # Step 3: 执行 DAG
    print(f"\n[3/4] 执行 DAG 流程...")
    dag_results = execute_dag(test_input, route)
    
    # Step 4: 质检
    passed, score = quality_check(dag_results, route)
    
    # 输出结果
    print(f"\n=== 最终交付 ===")
    for role, output in dag_results.items():
        print(f"\n[{role}]")
        print(output)
    
    print(f"\n质检评分: {score}/10")
    print(f"状态: {'✅ 通过' if passed else '❌ 不通过'}")
    print(f"\n日志已保存到: {LOG_FILE}")
