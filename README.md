# 🪄 魔法笔记本

一个模仿《哈利波特》魔法笔记本的交互网页应用。

在屏幕上用手指或笔写下问题 → 手写自动识别 → 大模型以魔法口吻回答 → 手写字体逐字浮现。

https://raw.githubusercontent.com/mmcxujie-cpu/magic-notebook/main/demo.mp4

点击 ▶️ 观看演示视频

## ✨ 功能

- ✏️ 手写输入（支持 iPad Apple Pencil 和手指）
- 🔍 百度 OCR 手写识别
- 🤖 DeepSeek AI 魔法风格回答
- ✍️ 打字机效果逐字浮现
- 🪄 魔法棒加载动画，点击可跳过
- 📖 历史记录页面（`/history`，每 10 秒自动刷新）

## 🚀 快速部署

```bash
# 1. 克隆
git clone https://github.com/mmcxujie-cpu/magic-notebook.git
cd magic-notebook

# 2. 启动
python3 server.py

# 3. 打开浏览器访问
# http://localhost:8080
```

> **DeepSeek API Key 已内置**（免费的，开箱即用）
> 只需要自己注册百度 OCR 即可（下面有教程）

## 🔑 配置百度 OCR（免费，必看）

魔法笔记本需要百度 OCR 来识别手写文字。免费注册只需 2 分钟：

### 注册步骤

1. 打开 [百度智能云 OCR 控制台](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)
2. 点击「**创建应用**」
3. 应用名称随意填，如「魔法笔记」
4. 勾选「**文字识别**」权限
5. 创建成功后，会得到 **API Key** 和 **Secret Key**

### 填入代码

打开 `server.py`，找到这两行：

```python
BAIDU_API_KEY = '你的百度API Key'
BAIDU_SECRET_KEY = '你的百度Secret Key'
```

替换成你刚才得到的 Key，保存即可。

> 免费额度：**每月 500 次**，个人使用完全够用。
> 不需要绑定银行卡，不需要充值。

## 📦 文件结构

```
server.py              服务器（含 DeepSeek Key，需填百度OCR Key）
魔法笔记本.html         前端页面（含字体，不需要修改）
font.woff2             王强书法体字库
history.json           历史记录（自动生成）
```

## 🛠 后台运行

```bash
nohup python3 server.py > server.log 2>&1 &
```

停止服务：
```bash
kill $(lsof -t -i:8080)
```

## ⚠️ 注意

- 服务器默认端口 **8080**，防火墙和安全组需要放行
- 历史记录存储在 `history.json`，最多保留 50 条
- 前端字体离线加载（woff2 内嵌），不需联网
