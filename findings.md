# 项目发现记录

## 当前环境

- 工作目录：`C:\Users\86157\Documents\New project`
- 当前是空 Git 项目，仅包含 `.git`。
- 用户希望从 0 到部署全过程协助。

## 产品决策

- 第一版选择 Python + FastAPI，原因是 Webhook 服务简单、部署选择多、后续接语音和 AI SDK 方便。
- 第一版先完成文本端到端闭环，语音与链接解析按可扩展接口设计。

## 待确认信息

- Telegram Bot Token。
- Notion Integration Token。
- Notion Database ID。
- LLM API Key 和模型名称。
- 语音识别服务商。

## 已实现决策

- AI 未配置时不会阻塞主流程，会生成“待整理”占位结果。
- AI 返回非 JSON 时会尝试从文本中提取 JSON 对象。
- Notion 字段采用固定字段名，README 中已列出需要创建的字段。
- Telegram 用户白名单通过 `TELEGRAM_ALLOWED_USER_IDS` 配置。
- 稳定部署优先选择 Railway，原因是官方支持 FastAPI、自动 HTTPS 域名、环境变量和健康检查；Render 作为备选。
- 用户选择不花钱后，部署策略调整为 GitHub + Render Free。接受休眠和冷启动，换取 $0 成本。

## 遇到的问题

| 问题 | 处理 |
|---|---|
| 本地服务运行时占用 `uvicorn.err.log` 和 `uvicorn.out.log` | 保持服务运行，日志文件已加入 `.gitignore` |
| 直接运行 `scripts/check_integrations.py` 时找不到 `app` 包 | 在脚本中加入项目根目录到 Python 搜索路径 |
| 用户提供的 Notion URL 是页面，不是内嵌数据库 | 使用 Notion 工具读取页面，找到真实数据库 ID 并更新 `.env` |
| Notion 数据库标题为空导致体检脚本 `IndexError` | 为数据库标题读取增加空列表兜底 |
| localhost.run 使用 `localhost:8000` 转发时公网请求空响应 | 改为明确转发 `127.0.0.1:8000`，公网健康检查通过 |
| 本机缺少 Railway CLI 和 GitHub CLI | 先补齐部署配置；实际上线需要用户提供 Railway 授权或在本机登录 CLI |
