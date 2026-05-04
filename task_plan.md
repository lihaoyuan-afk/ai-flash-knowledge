# AI 闪念知识库项目计划

## 项目目标

从 0 开始构建一个 Telegram Bot 驱动的个人知识收集系统：用户发送文字、语音或链接，服务端自动整理为标题、摘要、标签，并写入 Notion 数据库。

## 分工

### 我负责

- 设计并搭建项目代码结构。
- 实现 Telegram Webhook 接收逻辑。
- 实现文本消息处理主流程。
- 预留语音消息下载与转写接口。
- 实现 LLM 摘要、标题、标签提取模块。
- 实现 Notion 数据库写入模块。
- 提供本地运行、环境变量配置、部署说明。
- 添加基础测试和错误兜底，尽量避免灵感丢失。

### 你负责

- 在 Telegram 创建 Bot 并提供 `TELEGRAM_BOT_TOKEN`。
- 在 Notion 创建数据库、授权 Integration，并提供 `NOTION_TOKEN` 和 `NOTION_DATABASE_ID`。
- 选择并提供 LLM 服务商 API Key，第一版推荐使用 DeepSeek 兼容 OpenAI 的接口。
- 部署时选择平台，例如 Railway、Render、Vercel 或云服务器。
- 在部署完成后把公网 Webhook 地址告诉 Telegram。

## 技术路线

- 后端：Python + FastAPI
- 配置：`.env`
- Telegram：Webhook 模式
- LLM：OpenAI-compatible Chat Completions 接口，默认 DeepSeek
- Notion：官方 REST API
- 链接解析：MVP 先识别并保存链接，正文抓取放到后续版本

## 阶段计划

| 阶段 | 状态 | 目标 | 交付物 |
|---|---|---|---|
| 1. 项目初始化 | complete | 建立代码骨架和运行方式 | FastAPI 项目、依赖、配置模板 |
| 2. 文本主链路 | complete | 处理 Telegram 文本并写入 Notion | 文本消息端到端流程 |
| 3. AI 结构化 | complete | 生成标题、摘要、标签 | LLM 客户端和 JSON 解析兜底 |
| 4. Notion 写入 | complete | 保存结构化数据 | Notion 客户端 |
| 5. 语音支持 | partial | 下载语音并接入转写接口 | 音频处理接口与可配置转写实现 |
| 6. 本地与部署说明 | complete | 让用户能配置、运行、部署 | README 与环境变量说明 |
| 7. 验证 | complete | 基础测试与导入检查 | 测试命令和结果记录 |
| 8. 稳定部署准备 | complete | 准备 Railway/Render 部署文件 | 部署配置、依赖文件、部署说明 |
| 9. GitHub 推送 | pending | 推送代码到 GitHub 仓库 | 需要用户提供远程仓库 URL 或 GitHub 授权 |
| 10. Render Free 上线 | pending | 从 GitHub 自动部署到 Render Free 并替换 Telegram Webhook | 需要用户连接 Render 与 GitHub |

## MVP 范围

- 支持 Telegram 文本消息。
- 支持 URL 识别和保存，不抓取正文。
- 支持 Telegram 语音消息的流程入口，但转写服务可以按 API Key 后续接入。
- AI 失败时保存原文和失败状态，避免丢内容。
- Bot 返回成功或失败反馈。

## 风险与决策

- Telegram、Notion、LLM 都依赖外部密钥，代码先做配置校验和友好报错。
- Notion Multi-select 标签如果不存在，Notion API 通常可自动创建，仍需数据库字段名称完全匹配。
- 链接正文抓取复杂度高，第一版不作为阻塞项。

## 当前需要用户提供

- 稳定公网部署地址，用于替换当前临时隧道地址。
- 如果要验证 Telegram 主动回复，需要先在 Telegram 里给 Bot 发送 `/start` 或任意一句话。

## 当前验证状态

- LLM：已通过。
- Telegram Bot：已通过 `getMe` 验证。
- Notion API：已通过。
- LLM 到 Notion 写入：已通过，已创建一条联调测试记录。
- Telegram Webhook 端到端：已通过临时 HTTPS 隧道验证。
- 生产部署：待选择稳定部署平台。
