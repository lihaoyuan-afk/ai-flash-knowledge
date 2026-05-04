# 配置清单

## 1. `.env` 需要填写

```env
TELEGRAM_BOT_TOKEN=从 BotFather 拿到
TELEGRAM_ALLOWED_USER_IDS=你的 Telegram 数字用户 ID

NOTION_TOKEN=从 Notion Integration 拿到
NOTION_DATABASE_ID=Notion 数据库 ID

LLM_API_KEY=你刚刚提供的 LLM Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

## 2. Notion 数据库字段

字段名必须完全一致：

| 字段名 | 类型 |
|---|---|
| Name | Title |
| Tags | Multi-select |
| Summary | Text |
| Original Content | Text |
| Type | Select |
| Status | Select |
| Source URL | URL |
| Answer | Text |

`Type` 建议先建这些选项：

- Text
- Audio
- Link
- Image Question

`Status` 建议先建这些选项：

- Success
- AI Failed
- Empty

## 3. 验证命令

```powershell
python scripts/check_integrations.py
```

全部正常时会看到 LLM、Notion、Telegram 三项都是 `OK`。

如果要确认自己的 Telegram 用户 ID，先给 Bot 发一条消息，然后运行：

```powershell
python scripts/show_telegram_updates.py
```

## 4. 本地服务

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 5. Webhook

需要公网地址，例如 ngrok 或部署平台域名：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的 Bot Token"
$env:TELEGRAM_WEBHOOK_URL="https://你的公网域名/telegram/webhook"
python scripts/set_telegram_webhook.py
```
