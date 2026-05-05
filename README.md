# AI 闪念知识库

一个 Telegram-to-Notion 的个人知识收集服务。你在 Telegram 里发送文字、语音或链接，服务端会整理标题、摘要、标签，并写入 Notion 数据库。

## 当前 MVP 能力

- 接收 Telegram Webhook。
- 处理文本消息。
- 识别文本里的 URL，并按 Link 类型保存。
- 处理图片问题：用 Vertex AI Gemini 读取图片并生成答案，保存到 Notion 的 `Answer` 字段。
- 调用 LLM 生成标题、摘要、标签。
- 写入 Notion 数据库。
- AI 未配置或 AI 失败时，仍会保存原文并标记为待整理。
- 语音消息入口已预留，可接入兼容 `/audio/transcriptions` 的转写服务。

## 你需要准备

### 1. Telegram Bot Token

在 Telegram 找 `@BotFather`：

1. 发送 `/newbot`
2. 按提示创建 Bot
3. 复制 Bot Token，填入 `.env` 的 `TELEGRAM_BOT_TOKEN`

### 2. Notion Integration

在 Notion 开发者平台创建 Internal Integration，复制 Token，填入：

```env
NOTION_TOKEN=
```

然后在你的 Notion 数据库页面右上角把这个 Integration 邀请进去。

### 3. Notion 数据库字段

建议数据库包含这些字段，字段名要完全一致：

| 字段名 | 类型 |
|---|---|
| Name | Title |
| Tags | Multi-select |
| Summary | Text |
| Original Content | Text |
| Type | Select，选项：Text、Audio、Link |
| Status | Select，选项：Success、AI Failed、Empty |
| Source URL | URL |
| Answer | Text |

`Created Time` 可以用 Notion 自带的 Created time 字段。

### 4. LLM API Key

默认按 DeepSeek 的 OpenAI-compatible 接口配置：

```env
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

如果你使用其他兼容 Chat Completions 的服务，替换 `LLM_BASE_URL` 和 `LLM_MODEL` 即可。

## 本地运行

复制配置文件：

```powershell
Copy-Item .env.example .env
```

安装依赖：

```powershell
python -m pip install -e .
```

启动服务：

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

检查服务：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 检查外部服务配置

填好 `.env` 后运行：

```powershell
python scripts/check_integrations.py
```

它会分别检查 LLM、Notion 和 Telegram 是否可用。

做一次真实 Notion 写入测试：

```powershell
python scripts/smoke_test_write.py
```

## 设置 Telegram Webhook

本地调试时需要一个公网地址，可以用 ngrok、Cloudflare Tunnel 或部署平台给出的域名。

假设公网地址是：

```text
https://your-domain.example.com/telegram/webhook
```

设置环境变量并运行：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的 Bot Token"
$env:TELEGRAM_WEBHOOK_URL="https://your-domain.example.com/telegram/webhook"
python scripts/set_telegram_webhook.py
```

## 隐私保护

如果只允许你自己的 Telegram 账号使用，填：

```env
TELEGRAM_ALLOWED_USER_IDS=123456789
```

多个用户用英文逗号分隔。

如果不知道自己的 Telegram 数字 ID，先给 Bot 发一条消息，然后运行：

```powershell
python scripts/show_telegram_updates.py
```

更简短的逐项配置清单见：[docs/setup-checklist.md](docs/setup-checklist.md)

## 后续路线

- 接入稳定的语音识别服务。
- 增加链接正文抓取和正文清洗。
- 增加失败重试队列，进一步避免 Notion 写入失败导致丢失。
- 增加部署模板，例如 Railway 或 Docker。

免费部署说明见：[docs/deploy-render-free.md](docs/deploy-render-free.md)

Google Cloud Run 部署说明见：[docs/deploy-google-cloud-run.md](docs/deploy-google-cloud-run.md)

Railway 付费稳定部署说明见：[docs/deploy-railway.md](docs/deploy-railway.md)

## 使用图片问答

在 Telegram 里直接发送一张包含题目或问题的图片，可以附带一句 caption。Bot 会：

- 读取图片里的问题
- 生成完整答案
- 把题目/问题保存到 `Original Content`
- 把完整回答保存到 `Answer`
- 将 `Type` 标记为 `Image Question`

图片问答 provider 可以切换：

```env
IMAGE_ANSWER_PROVIDER=vertex
```

或者使用小米 OpenAI-compatible 视觉接口：

```env
IMAGE_ANSWER_PROVIDER=xiaomi
XIAOMI_API_KEY=
XIAOMI_BASE_URL=
XIAOMI_MODEL=
```
