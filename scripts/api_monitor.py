import json
import urllib.request
import time
import os

CONFIG_PATH = '/Users/apple/.openclaw/openclaw.json'
LOG_PATH = '/Users/apple/.openclaw/workspace/memory/ops/monitor.log'

def check_provider(provider_name, test_model):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        provider = cfg.get('models', {}).get('providers', {}).get(provider_name, {})
        base_url = provider.get('baseUrl', '').rstrip('/')
        api_key = provider.get('apiKey', '')
        
        if not base_url or not api_key:
            return False

        url = f"{base_url}/chat/completions"
        payload = {
            "model": test_model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        # 10秒超时（3秒太容易误杀，10秒既能挡住死节点，又能给偶尔的网络波动留余地）
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                return True
    except Exception as e:
        print(f"[{provider_name}] 检测失败: {e}")
        pass
    return False

def update_config(target_model):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        
    changed = False
    
    current_primary = cfg.get('agents', {}).get('defaults', {}).get('model', {}).get('primary')
    if current_primary != target_model:
        cfg['agents']['defaults']['model']['primary'] = target_model
        changed = True
        
    for a in cfg.get('agents', {}).get('list', []):
        if a.get('id') == 'jimmy':
            if a.get('model') != target_model:
                a['model'] = target_model
                changed = True
            break
            
    if changed:
        ts = time.strftime("%Y%m%d-%H%M%S")
        os.system(f"cp {CONFIG_PATH} {CONFIG_PATH}.bak-monitor-{ts}")
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            
        os.system("openclaw gateway restart")
        
        log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 监控探针触发: 自动切换主模型至 {target_model}\n"
        with open(LOG_PATH, 'a') as log:
            log.write(log_msg)
        print(log_msg.strip())
        return True
    return False

def main():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    # 优先级 1: 测试 Opus (mynewapi)
    if check_provider('mynewapi', 'claude-opus-4-6'):
        update_config('mynewapi/claude-opus-4-6')
        print("状态: Opus 正常，已确保在其主位。")
        return

    # 优先级 2: 测试 GPT-5.4 (mygptapi)
    if check_provider('mygptapi', 'gpt-5.4'):
        update_config('mygptapi/gpt-5.4')
        print("状态: Opus 离线，GPT-5.4 正常，切至 GPT-5.4。")
        return
        
    # 优先级 3: 都挂了，退守 Gemini Flash
    update_config('geminiflash/gemini-3-flash-preview')
    print("状态: 主力全挂，已紧急退守 Gemini Flash 兜底。")

if __name__ == '__main__':
    main()