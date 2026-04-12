#!/usr/bin/env python3
"""xjrouter HTTP 反向代理 v3 — SSE 聚合 + 流式透传"""
import http.server
import http.client
import socketserver
import json
import sys
import time
import uuid

LISTEN_PORT = 8444
UPSTREAM_HOST = "47.86.25.153"
UPSTREAM_PORT = 80
VIRTUAL_HOST = "xjrouter.xyz"
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 600

HOP_BY_HOP = frozenset([
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers',
    'transfer-encoding', 'upgrade'
])


class ProxyHandler(http.server.BaseHTTPRequestHandler):

    @staticmethod
    def _fix_messages(data):
        """content 数组转字符串 + developer→system（双保险）"""
        if 'messages' not in data:
            return
        for msg in data['messages']:
            # developer role → system（xjrouter 不认 developer）
            if msg.get('role') == 'developer':
                msg['role'] = 'system'
            content = msg.get('content')
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        parts.append(item.get('text', ''))
                    elif isinstance(item, str):
                        parts.append(item)
                msg['content'] = '\n'.join(parts) if parts else ''

    @staticmethod
    def _aggregate_sse(resp):
        """读取 SSE 流，聚合成完整的非流式 OpenAI 响应"""
        text_parts = {}  # index -> text
        reasoning_parts = {}  # index -> reasoning
        tool_calls = {}  # index -> {id, type, function: {name, arguments}}
        stop_reason = "stop"
        model = ""
        resp_id = ""
        usage = {}

        for line in resp:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace')
            line = line.rstrip('\r\n')

            if not line.startswith('data:'):
                continue

            data_str = line[5:].strip()
            if data_str == '[DONE]':
                break

            try:
                ev = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            if ev.get('id'):
                resp_id = ev['id']
            if ev.get('model'):
                model = ev['model']

            choices = ev.get('choices', [])
            for ch in choices:
                idx = ch.get('index', 0)
                delta = ch.get('delta', {})

                # 文本内容
                content = delta.get('content')
                if content:
                    text_parts.setdefault(idx, []).append(content)

                # reasoning_content
                reasoning = delta.get('reasoning_content')
                if reasoning:
                    reasoning_parts.setdefault(idx, []).append(reasoning)

                # tool_calls（流式增量聚合）
                for tc in delta.get('tool_calls', []):
                    tc_idx = tc.get('index', 0)
                    if tc_idx not in tool_calls:
                        tool_calls[tc_idx] = {
                            'id': tc.get('id', ''),
                            'type': tc.get('type', 'function'),
                            'function': {'name': '', 'arguments': ''}
                        }
                    if tc.get('id'):
                        tool_calls[tc_idx]['id'] = tc['id']
                    if tc.get('type'):
                        tool_calls[tc_idx]['type'] = tc['type']
                    fn = tc.get('function', {})
                    if fn.get('name'):
                        tool_calls[tc_idx]['function']['name'] += fn['name']
                    if fn.get('arguments'):
                        tool_calls[tc_idx]['function']['arguments'] += fn['arguments']

                # finish_reason
                fr = ch.get('finish_reason')
                if fr:
                    stop_reason = fr

            # usage
            if ev.get('usage'):
                usage = ev['usage']

        # 拼装非流式响应
        final_text = ''.join(text_parts.get(0, []))
        final_reasoning = ''.join(reasoning_parts.get(0, []))

        message = {
            "role": "assistant",
            "content": final_text
        }
        if tool_calls:
            message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls.keys())]
            if not final_text:
                message["content"] = None

        result = {
            "id": resp_id or f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": message,
                "finish_reason": stop_reason
            }]
        }
        if final_reasoning:
            result["choices"][0]["message"]["reasoning_content"] = final_reasoning
        if usage:
            result["usage"] = usage

        return result

    def _proxy(self, method):
        try:
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len) if content_len > 0 else None

            # 解析请求，判断客户端是否要流式
            client_wants_stream = True
            data = None
            if body and method == 'POST':
                try:
                    data = json.loads(body)
                    client_wants_stream = data.get('stream', True)
                    # 记录完整请求（截断到2000字符）
                    body_str = body.decode('utf-8', errors='replace')[:2000]
                    sys.stderr.write(f"[proxy] client stream={client_wants_stream}, model={data.get('model','?')}, body_len={len(body)}\n")
                    sys.stderr.write(f"[proxy] request keys: {list(data.keys())}\n")
                    sys.stderr.flush()
                    # 修复 content 格式
                    self._fix_messages(data)
                    # 清理 xjrouter 不支持的字段（保留 tools/tool_choice/parallel_tool_calls）
                    for bad_key in ('stream_options', 'store'):
                        data.pop(bad_key, None)
                    # max_completion_tokens → max_tokens（兼容旧 API）
                    if 'max_completion_tokens' in data and 'max_tokens' not in data:
                        data['max_tokens'] = data.pop('max_completion_tokens')
                    elif 'max_completion_tokens' in data:
                        data.pop('max_completion_tokens')
                    # 强制上游流式（绕过 xjrouter 非流式 bug）
                    data['stream'] = True
                    body = json.dumps(data, ensure_ascii=False).encode()
                    sys.stderr.write(f"[proxy] AFTER cleanup keys: {list(data.keys())}, body_len={len(body)}\n")
                    # dump 实际发送的 body 到文件用于调试
                    with open('/tmp/xjrouter-last-request.json', 'wb') as df:
                        df.write(body)
                    # 打印 messages 结构摘要
                    for i, m in enumerate(data.get('messages', [])):
                        c = m.get('content')
                        ctype = type(c).__name__
                        clen = len(json.dumps(c, ensure_ascii=False)) if c else 0
                        sys.stderr.write(f"[proxy]   msg[{i}] role={m.get('role')} content_type={ctype} content_len={clen}\n")
                        # 打印 message 的所有 keys
                        sys.stderr.write(f"[proxy]   msg[{i}] keys={list(m.keys())}\n")
                    sys.stderr.flush()
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass

            conn = http.client.HTTPConnection(
                UPSTREAM_HOST, UPSTREAM_PORT,
                timeout=CONNECT_TIMEOUT
            )

            fwd_headers = {'Host': VIRTUAL_HOST}
            for key, val in self.headers.items():
                lk = key.lower()
                if lk in ('host', 'content-length'):
                    continue
                if lk not in HOP_BY_HOP:
                    fwd_headers[key] = val
            if body is not None:
                fwd_headers['Content-Length'] = str(len(body))
            
            sys.stderr.write(f"[proxy] forwarding headers: {dict(fwd_headers)}\n")
            sys.stderr.flush()

            conn.request(method, self.path, body=body, headers=fwd_headers)
            conn.sock.settimeout(READ_TIMEOUT)
            resp = conn.getresponse()

            sys.stderr.write(f"[proxy] upstream status={resp.status}, content-type={resp.getheader('Content-Type')}\n")
            if resp.status >= 400:
                err_body = resp.read()
                sys.stderr.write(f"[proxy] upstream error: {err_body[:500]}\n")
                sys.stderr.flush()
                self.send_response(resp.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
                conn.close()
                return
            sys.stderr.flush()

            if not client_wants_stream and 'event-stream' in (resp.getheader('Content-Type') or ''):
                # 客户端要非流式，但上游返回了 SSE → 聚合后返回非流式 JSON
                sys.stderr.write(f"[proxy] aggregating SSE → non-stream JSON\n")
                sys.stderr.flush()
                result = self._aggregate_sse(resp)
                result_bytes = json.dumps(result, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(result_bytes)))
                self.end_headers()
                self.wfile.write(result_bytes)
            else:
                # 流式透传
                self.send_response(resp.status)
                for key, val in resp.getheaders():
                    lk = key.lower()
                    if lk not in HOP_BY_HOP:
                        self.send_header(key, val)
                self.end_headers()

                while True:
                    chunk = resp.read(1)
                    if not chunk:
                        break
                    more = resp.read(4095)
                    out = chunk + (more if more else b'')
                    self.wfile.write(out)
                    self.wfile.flush()

            conn.close()

        except Exception as e:
            try:
                error_body = json.dumps({"error": f"proxy error: {e}"}).encode()
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(error_body)))
                self.end_headers()
                self.wfile.write(error_body)
            except Exception:
                pass

    def do_POST(self):
        self._proxy('POST')

    def do_GET(self):
        self._proxy('GET')

    def do_OPTIONS(self):
        self._proxy('OPTIONS')

    def log_message(self, format, *args):
        # 开启调试日志
        sys.stderr.write(f"[proxy] {format % args}\n")
        sys.stderr.flush()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == '__main__':
    server = ThreadedHTTPServer(('127.0.0.1', LISTEN_PORT), ProxyHandler)
    print(f"🔄 xjrouter proxy v3 (SSE aggregate + stream passthrough) on http://127.0.0.1:{LISTEN_PORT}", flush=True)
    print(f"   → upstream: http://{UPSTREAM_HOST}:{UPSTREAM_PORT} (Host: {VIRTUAL_HOST})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹ proxy stopped", flush=True)
        server.shutdown()
