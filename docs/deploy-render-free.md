# Render Free 部署指南

## 方案

使用 GitHub 保存代码，Render 从 GitHub 仓库自动部署免费的 Web Service。

## 成本

Render Free Web Service 不需要月费，但有这些限制：

- 15 分钟没有请求会休眠。
- 下一次请求会触发冷启动，可能需要约 1 分钟。
- 免费实例可能重启，不适合严格生产场景。

对这个个人知识库 Bot 来说，可以先免费跑通；如果后续觉得第一条消息等待太久，再升级到付费实例。

## 已准备好的文件

- `render.yaml`：Render Blueprint，使用 `plan: free`
- `requirements.txt`：Python 依赖
- `.github/workflows/ci.yml`：GitHub 自动测试

## Render 环境变量

在 Render 的 Environment 页面填写：

```env
APP_ENV=production
TELEGRAM_BOT_TOKEN=你的 Telegram Bot Token
TELEGRAM_ALLOWED_USER_IDS=你的 Telegram 数字用户 ID
NOTION_TOKEN=你的 Notion Integration Token
NOTION_DATABASE_ID=356dfe08d9eb80519c07fea5a5d07ee7
LLM_API_KEY=你的 LLM API Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

语音识别暂时不填：

```env
TRANSCRIPTION_API_KEY=
TRANSCRIPTION_BASE_URL=
TRANSCRIPTION_MODEL=
```

## 部署步骤

1. 把本项目推送到 GitHub。
2. 登录 Render。
3. 选择 New -> Blueprint 或 Web Service。
4. 连接 GitHub 仓库。
5. 如果使用 Blueprint，Render 会读取 `render.yaml`。
6. 填写环境变量。
7. 部署完成后，打开 Render 给的 HTTPS 域名并访问 `/health`。

## 设置 Telegram Webhook

假设 Render 域名是：

```text
https://ai-flash-knowledge.onrender.com
```

运行：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的 Telegram Bot Token"
$env:TELEGRAM_WEBHOOK_URL="https://ai-flash-knowledge.onrender.com/telegram/webhook"
python scripts/set_telegram_webhook.py
```

确认：

```powershell
Invoke-RestMethod "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"
```
