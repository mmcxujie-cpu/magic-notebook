[🇨🇳 中文](README.md) | [🇬🇧 English](README.en.md)

---

# 🪄 Magic Notebook

An interactive web app that mimics the magical notebook from *Harry Potter*.

Write your question on the screen with your finger or stylus → handwriting is recognized by OCR → AI answers in a magical tone → answer appears character by character in a handwritten font.



https://github.com/user-attachments/assets/229dac5d-0bbd-4d92-bddd-419bff7917ba



## ✨ Features

- ✏️ Handwriting input (supports iPad Apple Pencil and finger)
- 🔍 Baidu OCR handwriting recognition (free)
- 🤖 DeepSeek AI answers in a mysterious, magical style
- ✍️ Typewriter effect — characters appear one by one
- 🪄 Loading animation (click the magic wand to skip)
- 📖 History page at `/history` (auto-refresh every 60s)

## 🚀 Quick Start

```bash
git clone https://github.com/mmcxujie-cpu/magic-notebook.git
cd magic-notebook
python3 server.py
```

Open **http://localhost:8080** in your browser.

> DeepSeek API key is included (free, works out of the box).
> You only need to register your own Baidu OCR key (free, see below).

## 🔑 Configure Baidu OCR (Free)

1. Go to [Baidu AI OCR Console](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)
2. Click **"Create Application"**
3. Name it anything (e.g., "Magic Notebook")
4. Enable **"Text Recognition"** permission
5. Copy the **API Key** and **Secret Key**

Open `server.py` and replace:

```python
BAIDU_API_KEY = 'your-baidu-api-key'
BAIDU_SECRET_KEY = 'your-baidu-secret-key'
```

> Free tier: **500 requests per month**, no credit card required.

## 📦 File Structure

| File | Description |
|------|-------------|
| `server.py` | Python server (DeepSeek key included) |
| `魔法笔记本.html` | Frontend page (no modification needed) |
| `font.woff2` | Handwriting font |
| `demo.mp4` | Demo video |
| `demo-thumb.jpg` | Video thumbnail |
| `history.json` | History records (auto-generated) |

## 🛠 Run in Background

```bash
nohup python3 server.py > server.log 2>&1 &
```

Stop:
```bash
kill $(lsof -t -i:8080)
```

## ⚠️ Notes

- Default port: **8080**. Make sure your firewall allows it.
- History is stored in `history.json` (max 50 records).
- The font is embedded (woff2), no internet needed.
