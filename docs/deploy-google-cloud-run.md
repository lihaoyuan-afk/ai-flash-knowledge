# Google Cloud Run 部署指南

## 方案

使用 Google Cloud Run 部署 FastAPI Webhook 服务。

Cloud Run 适合这个项目，因为它提供：

- 自动 HTTPS 公网地址
- 按请求弹性运行
- 可以缩容到 0，低频使用成本很低
- 支持 Dockerfile 和 GitHub 源码部署

## 成本提醒

Cloud Run 有免费额度，但 Google Cloud 通常需要绑定结算账号。个人低频 Bot 很可能落在免费额度内，但仍建议：

- 开启 Budget 和账单提醒
- 设置 Cloud Run 最大实例数，例如 1
- 不配置最小实例数，保持可缩容到 0

免费部署的代价是冷启动：长时间没人发消息后，第一次 Telegram 请求可能慢一点。

## 已准备文件

- `Dockerfile`
- `.dockerignore`
- `requirements.txt`

## 推荐区域

建议使用：

```text
us-central1
```

这是常见低成本区域，也便于使用 Cloud Run 免费额度。

## 需要的环境变量

部署时设置：

```env
APP_ENV=production
TELEGRAM_BOT_TOKEN=你的 Telegram Bot Token
TELEGRAM_ALLOWED_USER_IDS=8271129015
NOTION_TOKEN=你的 Notion Integration Token
NOTION_DATABASE_ID=356dfe08d9eb80519c07fea5a5d07ee7
LLM_API_KEY=你的 LLM API Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
VERTEX_AI_PROJECT=project-e31ce97f-79c3-4153-abb
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.5-flash
```

Cloud Run 运行服务账号需要有 Vertex AI User 权限：

```powershell
gcloud projects add-iam-policy-binding project-e31ce97f-79c3-4153-abb `
  --member="serviceAccount:189424783668-compute@developer.gserviceaccount.com" `
  --role="roles/aiplatform.user"
```

语音识别暂时不设置。

## 使用 Cloud Shell 部署

在 Google Cloud Console 打开 Cloud Shell，进入仓库后运行：

```bash
gcloud run deploy ai-flash-knowledge \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --max-instances 1 \
  --set-env-vars APP_ENV=production,LLM_BASE_URL=https://api.deepseek.com,LLM_MODEL=deepseek-chat,NOTION_DATABASE_ID=356dfe08d9eb80519c07fea5a5d07ee7,TELEGRAM_ALLOWED_USER_IDS=8271129015
```

密钥类变量建议在 Console 页面里填写，避免出现在命令历史中：

- `TELEGRAM_BOT_TOKEN`
- `NOTION_TOKEN`
- `LLM_API_KEY`

## 部署后验证

部署成功后 Cloud Run 会输出 Service URL，例如：

```text
https://ai-flash-knowledge-xxxxx-uc.a.run.app
```

健康检查：

```bash
curl https://你的-cloud-run-url/health
```

设置 Telegram Webhook：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的 Telegram Bot Token"
$env:TELEGRAM_WEBHOOK_URL="https://你的-cloud-run-url/telegram/webhook"
python scripts/set_telegram_webhook.py
```

确认：

```powershell
Invoke-RestMethod "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo"
```
