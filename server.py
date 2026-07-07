#!/usr/bin/env python3
"""🪄 魔法笔记本 - Magic Notebook 服务器"""
import http.server
import urllib.request
import urllib.parse
import json
import os
import time
import html as html_mod

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

# ====== API Key 配置 ======
# DeepSeek（免费，内置可直接使用）
DEEPSEEK_API_KEY = 'sk-QLsE98ACQ03rQ58L7850D6A23c3d45B3A1678cC487E45054'

# 百度 OCR（需要自己注册免费替换）
# 注册地址：https://console.bce.baidu.com/ai/#/ai/ocr/overview/index
BAIDU_API_KEY = '你的百度API Key'
BAIDU_SECRET_KEY = '你的百度Secret Key'
# ==========================

HISTORY_FILE = os.path.join(DIR, 'history.json')
_history = []

def load_history():
    global _history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                _history = json.load(f)
        except:
            _history = []

def save_history():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(_history, f, ensure_ascii=False, indent=2)

def add_history(record):
    load_history()
    _history.insert(0, record)
    if len(_history) > 50:
        _history.pop()
    save_history()

_baidu_token = None
_baidu_token_expiry = 0

def get_baidu_token():
    global _baidu_token, _baidu_token_expiry
    if _baidu_token and time.time() < _baidu_token_expiry:
        return _baidu_token
    if BAIDU_API_KEY == '你的百度API Key':
        return None
    url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={BAIDU_API_KEY}&client_secret={BAIDU_SECRET_KEY}'
    req = urllib.request.Request(url, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        j = json.loads(resp.read())
    _baidu_token = j['access_token']
    _baidu_token_expiry = time.time() + j['expires_in'] - 60
    return _baidu_token


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/ocr-proxy':
            self.handle_ocr()
        elif self.path == '/deepseek-proxy':
            self.handle_deepseek()
        elif self.path == '/api/history':
            self.handle_history_post()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/history':
            self.handle_history_page()
        elif self.path == '/api/history':
            self.handle_history_get()
        else:
            super().do_GET()

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else b''

    def handle_ocr(self):
        try:
            body = self._read_body()
            params = urllib.parse.parse_qs(body.decode())
            image_data = params.get('image', [''])[0]
            if not image_data:
                self._send_json(400, {'error': 'missing image'})
                return
            token = get_baidu_token()
            if not token:
                self._send_json(200, {'error_msg': '请先配置百度OCR API Key', 'error_code': 999})
                return
            baidu_data = urllib.parse.urlencode({
                'image': image_data, 'detect_direction': 'false', 'probability': 'false'
            }).encode()
            url = f'https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token={token}'
            req = urllib.request.Request(url, data=baidu_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = resp.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(result)
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    def handle_deepseek(self):
        try:
            body = self._read_body()
            req_data = json.loads(body)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
            }
            req = urllib.request.Request(
                'https://api.edgefn.net/v1/chat/completions',
                data=json.dumps(req_data).encode(), headers=headers)
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
            resp.close()
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    def handle_history_post(self):
        try:
            body = self._read_body()
            data = json.loads(body)
            add_history(data)
            self._send_json(200, {'ok': True})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    def handle_history_get(self):
        load_history()
        self._send_json(200, _history)

    def handle_history_page(self):
        load_history()
        html_content = self._render_history_page()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def _render_history_page(self):
        items = ''
        for i, rec in enumerate(_history):
            q = html_mod.escape(rec.get('question', ''))
            a = html_mod.escape(rec.get('answer', ''))
            t = rec.get('time', '')[:19].replace('T', ' ')
            img = rec.get('snapshotUrl', '')
            img_tag = f'<img src="{img}" style="max-width:300px;max-height:120px;border-radius:4px;">' if img else ''
            items += f'''<div class="entry"><div class="meta">#{len(_history)-i} · {t}</div><div class="row"><div class="col-img">{img_tag}</div><div class="col-text"><div class="label">✏️ 识别文字</div><div class="val">{q}</div><div class="label">🪄 魔法回答</div><div class="val">{a}</div></div></div></div>'''
        return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><meta http-equiv="refresh" content="10"><title>魔法笔记本 · 历史记录</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#0a0a0a;color:#e0d8c8;font-family:'LXGW WenKai','STKaiti',cursive;padding:30px;max-width:900px;margin:0 auto}}h1{{text-align:center;font-size:28px;margin-bottom:30px;color:#ffffff;letter-spacing:4px}}.entry{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;margin-bottom:20px}}.meta{{font-size:13px;color:rgba(255,255,255,0.3);margin-bottom:12px}}.row{{display:flex;gap:20px;align-items:flex-start}}.col-img{{flex-shrink:0}}.col-img img{{border:1px solid rgba(255,255,255,0.1);max-width:300px;max-height:120px;border-radius:4px}}.col-text{{flex:1;min-width:0}}.label{{font-size:13px;color:rgba(255,255,255,0.4);margin-top:8px}}.label:first-child{{margin-top:0}}.val{{font-size:17px;color:#ffffff;line-height:1.6;margin-bottom:4px;word-break:break-word;white-space:pre-wrap}}.empty{{text-align:center;color:rgba(255,255,255,0.2);margin-top:80px;font-size:18px}}.footer{{text-align:center;margin-top:40px;color:rgba(255,255,255,0.15);font-size:13px}}@media(max-width:600px){{.row{{flex-direction:column}}.col-img img{{max-width:100%!important}}}}</style></head><body><h1>📖 魔法笔记本 · 记录</h1>{"".join(items) if items else '<div class="empty">暂无记录，写下你的第一个问题吧 ✏️</div>'}<div class="footer">本地存储 · 最多 50 条</div></body></html>'''

    def log_message(self, fmt, *args):
        try:
            msg = fmt % args
        except:
            msg = str(args)
        print(f"[魔法笔记本] {msg}")

if __name__ == '__main__':
    os.chdir(DIR)
    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'🪄 魔法笔记本服务器已启动 → http://0.0.0.0:{PORT}/')
    print(f'📖 历史记录 → http://0.0.0.0:{PORT}/history')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        server.server_close()