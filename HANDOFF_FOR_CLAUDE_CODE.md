# AI 闪念知识库交接文档

## 项目概况

项目名：AI 闪念知识库 / Chat-to-Notion

目标：用户在 Telegram Bot 里发送文字、链接或语音，服务端自动调用 LLM 生成标题、摘要、标签，并写入 Notion 数据库。

本地目录：

```text
C:\Users\86157\Documents\New project
```

GitHub 仓库：

```text
https://github.com/lihaoyuan-afk/ai-flash-knowledge
```

当前主分支：

```text
main
```

## 当前架构

- 后端：Python + FastAPI
- Webhook：Telegram Bot Webhook
- AI：DeepSeek OpenAI-compatible Chat Completions
- 存储：Notion API
- 部署目标：Google Cloud Run
- 免费备选：Render Free，但用户反馈尝试失败

## 已完成

1. FastAPI 服务已完成。
2. Telegram 文本、链接、语音消息入口解析已完成。
3. LLM 结构化提取已完成。
4. Notion 写入已完成。
5. Notion 数据库字段已补齐。
6. 本地端到端验证成功。
7. 临时 HTTPS 隧道端到端验证成功。
8. GitHub 仓库已创建并推送。
9. Render Free 配置已创建。
10. Google Cloud Run 部署文件已创建。
11. Google Cloud Run 服务已部署成功。

## 关键文件

```text
app/main.py                 FastAPI 入口
app/service.py              主业务流程
app/telegram.py             Telegram Update 解析和回复
app/llm.py                  LLM 提取标题、摘要、标签
app/notion.py               Notion 写入
app/transcription.py        语音转写接口
app/config.py               环境变量配置

scripts/check_integrations.py     检查 LLM / Notion / Telegram
scripts/set_telegram_webhook.py   设置 Telegram Webhook
scripts/smoke_test_write.py       LLM -> Notion 写入测试

Dockerfile
.dockerignore
requirements.txt
render.yaml
railway.json
Procfile

docs/deploy-google-cloud-run.md
docs/deploy-render-free.md
docs/deploy-railway.md
docs/setup-checklist.md
```

## 环境变量

真实密钥在本地 `.env` 中，`.env` 已被 `.gitignore` 忽略，不要提交。

需要的环境变量：

```env
APP_ENV=production
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_IDS=8271129015
NOTION_TOKEN=
NOTION_DATABASE_ID=356dfe08d9eb80519c07fea5a5d07ee7
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
VERTEX_AI_PROJECT=project-e31ce97f-79c3-4153-abb
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.5-flash
```

语音识别暂时未正式配置：

```env
TRANSCRIPTION_API_KEY=
TRANSCRIPTION_BASE_URL=
TRANSCRIPTION_MODEL=
```

## Notion 信息

用户原始 Notion 页面：

```text
https://www.notion.so/AI-356dfe08d9eb80d9afa2c3cde5319ca7
```

真实内嵌数据库 ID：

```text
356dfe08d9eb80519c07fea5a5d07ee7
```

数据库字段已补齐：

- `Name`：Title
- `Tags`：Multi-select
- `Summary`：Text
- `Original Content`：Text
- `Type`：Select，包含 `Text`、`Audio`、`Link`
- `Status`：Select，包含 `Success`、`AI Failed`、`Empty`
- `Source URL`：URL

## 已验证记录

本地和临时隧道曾成功写入 Notion，示例记录：

- `联调测试-零摩擦闪念知识库联调`
- `Webhook连接Telegram与Notion`
- `Webhook与AI集成指南`

## Google Cloud 当前状态

本机已安装并登录 `gcloud`。

当前账号：

```text
zli638653@gmail.com
```

当前项目：

```text
project-e31ce97f-79c3-4153-abb
```

已启用服务：

- `run.googleapis.com`
- `cloudbuild.googleapis.com`
- `artifactregistry.googleapis.com`

已有 Cloud Run 服务：

```text
ai-flash-knowledge
```

区域：

```text
us-central1
```

Cloud Run URL：

```text
https://ai-flash-knowledge-dlno2syv4q-uc.a.run.app
```

另一个部署输出 URL 也可访问：

```text
https://ai-flash-knowledge-189424783668.us-central1.run.app
```

Telegram Webhook 已指向：

```text
https://ai-flash-knowledge-dlno2syv4q-uc.a.run.app/telegram/webhook
```

## 当前未解决问题

Cloud Run 服务已经部署，`/health` 返回正常，Webhook 模拟请求也返回 `ok`。

但是最近一次云端模拟消息：

```text
Google Cloud Run 云端联调：这条消息通过稳定公网服务进入 AI 闪念知识库并写入 Notion。
```

没有在 Notion 中查到对应记录。

判断：服务内部某一步失败，但旧代码会兜底吞异常并返回 `ok`。已经修改 `app/service.py`，加入 `logger.exception(...)`，用于在 Cloud Run 日志中看到具体失败原因。

重要：日志补丁已经部署到了 Cloud Run revision：

```text
ai-flash-knowledge-00003-xv6
```

但在用户中断前，还没有重新执行云端模拟消息并读取新日志。

## 下一步建议

### 1. 重新给 Cloud Run 设置密钥环境变量

最近一次 `gcloud run deploy --source .` 只设置了非密钥变量，可能覆盖/保留情况需要确认。建议重新显式更新密钥变量。

从本地 `.env` 读取并更新：

```powershell
$vars = @{}
Get-Content .env | ForEach-Object {
  if ($_ -match '^([^#=]+)=(.*)$') {
    $vars[$matches[1]] = $matches[2]
  }
}

$envArg = "TELEGRAM_BOT_TOKEN=$($vars['TELEGRAM_BOT_TOKEN']),NOTION_TOKEN=$($vars['NOTION_TOKEN']),LLM_API_KEY=$($vars['LLM_API_KEY'])"

gcloud run services update ai-flash-knowledge `
  --region us-central1 `
  --update-env-vars $envArg
```

### 2. 验证健康检查

```powershell
Invoke-RestMethod https://ai-flash-knowledge-dlno2syv4q-uc.a.run.app/health
```

期望：

```json
{"status":"ok"}
```

### 3. 重新模拟云端 Webhook

```powershell
$payload = @{
  message = @{
    message_id = 505
    chat = @{ id = 8271129015 }
    from = @{ id = 8271129015 }
    text = 'Cloud Run 日志验证：这条消息用于确认云端是否真正写入 Notion。'
  }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Uri 'https://ai-flash-knowledge-dlno2syv4q-uc.a.run.app/telegram/webhook' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $payload
```

### 4. 查询 Notion 是否写入

```powershell
@'
import asyncio
import httpx
from app.config import get_settings

async def main():
    s = get_settings()
    headers = {
        'Authorization': f'Bearer {s.notion_token}',
        'Notion-Version': s.notion_version,
        'Content-Type': 'application/json',
    }
    payload = {
        'filter': {
            'property': 'Original Content',
            'rich_text': {'contains': 'Cloud Run 日志验证'}
        },
        'page_size': 10,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f'https://api.notion.com/v1/databases/{s.notion_database_id}/query',
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
    print(len(r.json().get('results', [])))
    for page in r.json().get('results', []):
        props = page.get('properties', {})
        title = ''.join(part.get('plain_text','') for part in props.get('Name', {}).get('title', []))
        print(title, page.get('url'))

asyncio.run(main())
'@ | python -
```

### 5. 如果没写入，读取 Cloud Run 日志

```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-flash-knowledge" `
  --limit 50 `
  --format="value(timestamp,textPayload)"
```

重点找：

```text
Failed to handle incoming content
```

如果日志显示 Notion 401/403：

- 检查 Cloud Run 的 `NOTION_TOKEN`
- 检查 Notion Integration 是否仍被邀请到数据库页面

如果日志显示 LLM 401/402：

- 检查 `LLM_API_KEY`
- 检查 DeepSeek 余额

如果日志显示 Telegram sendMessage 失败：

- 不影响入库，因为 `_safe_send` 已兜底

## Git 状态

在用户中断时，新增的 Google Cloud 文件和日志补丁尚未提交到 GitHub。

建议先执行：

```powershell
git status --short
python -m pytest
python -m compileall app scripts
git add .
git commit -m "Add Google Cloud Run deployment support"
git push
```

提交前确认：

```powershell
git check-ignore -v .env
```

还可以扫描密钥：

```powershell
$patterns = @('sk-[A-Za-z0-9]', 'ntn_', '[0-9]{8,}:[A-Za-z0-9_-]{20,}')
$files = Get-ChildItem -Recurse -File -Force | Where-Object {
  $_.FullName -notmatch '\\.git\\|\\.env$|\\.pytest_cache\\|__pycache__|\.log$'
}
$matches = foreach ($file in $files) {
  Select-String -Path $file.FullName -Pattern $patterns -AllMatches -ErrorAction SilentlyContinue
}
if ($matches) {
  $matches | Select-Object Path, LineNumber, Line
} else {
  'NO_SECRET_MATCHES'
}
```

## 成本提醒

Google Cloud Run 有免费额度，但通常需要绑定结算账号。建议用户做两件事：

1. 设置 Billing Budget 和提醒。
2. Cloud Run 保持 `--max-instances 1`，不要设置 `min-instances`，让服务可缩容到 0。

## 参考文档

- Google Cloud Run pricing: https://cloud.google.com/run/pricing
- Deploy from source: https://cloud.google.com/run/docs/deploying-source-code
- gcloud run deploy: https://cloud.google.com/sdk/gcloud/reference/run/deploy
