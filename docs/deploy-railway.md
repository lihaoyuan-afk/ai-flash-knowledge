# Railway 稳定部署指南

## 为什么选 Railway

这个项目是一个 Webhook 小服务，需要：

- 稳定 HTTPS 公网域名
- 能长期运行的 Web Service
- 环境变量管理
- `/health` 健康检查

Railway 官方 FastAPI 指南支持从 GitHub、CLI 或 Dockerfile 部署；公共网络可以直接生成 Railway 域名，并自动提供 SSL。

## 已准备好的部署文件

- `requirements.txt`：部署依赖
- `railway.json`：Railway 启动命令和健康检查
- `Procfile`：通用 Web 服务启动命令
- `render.yaml`：Render 备选部署配置

## Railway 需要设置的环境变量

不要把真实密钥写进 Git 仓库，在 Railway 的 Variables 页面填写：

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

语音识别暂时可以不填：

```env
TRANSCRIPTION_API_KEY=
TRANSCRIPTION_BASE_URL=
TRANSCRIPTION_MODEL=
```

## 部署后验证

假设 Railway 生成的域名是：

```text
https://your-service.up.railway.app
```

健康检查：

```powershell
Invoke-RestMethod https://your-service.up.railway.app/health
```

设置 Telegram Webhook：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的 Telegram Bot Token"
$env:TELEGRAM_WEBHOOK_URL="https://your-service.up.railway.app/telegram/webhook"
python scripts/set_telegram_webhook.py
```

确认 Webhook：

```powershell
Invoke-RestMethod "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

## 我需要你提供的授权

为了由我继续完成自动部署，你任选一种：

1. Railway：提供 Railway Project Token，或在本机登录 Railway CLI。
2. GitHub + Railway：提供 GitHub 仓库权限，并在 Railway 里授权部署该仓库。
3. Render：提供 Render API Key，或在 Render 页面创建 Web Service 后把服务地址发给我。

我推荐第 1 种，最快。
