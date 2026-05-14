# PR 集成记录

> 记录日期：2026-05-14  
> 当前基线：`main` 已快进合并 `codex/stable-pr-integration`，最新稳定集成提交为 `afa8c72 合并稳定 PR 基础修复`。

本文档记录本轮已经合入本地 `main` 的 PR、明确未合入的 PR，以及后续继续合并时的注意事项。

## 已合入 main

| PR | 合入方式 | 功能与用途 | 备注 |
|---|---|---|---|
| #60 fix API Key 自定义 model_provider | 完整合入 | 修复 API Key 模式下自定义 provider / 中转端点被插件解锁逻辑误改为 `chatgpt`，导致 API Key 不发送的问题；同时保留自定义 `base_url` 主机加入 `NO_PROXY` 的逻辑。 | 属于本轮稳定基础修复。 |
| #82 本地代理注入改为显式开启 | 手工整合 | 新增 `launch --proxy`；默认不再自动探测并注入本地代理，只有显式传参时才注入代理环境变量。 | 已和 #60 的 `NO_PROXY` 策略合并：默认不注入代理，但仍为自定义 provider 主机补 `NO_PROXY`。 |
| #10 macOS 二次打开不响应修复 | 部分摘取 | 摘取 macOS/CLI 相关修复：`.app` launcher 后台启动、helper 端口占用时检查 `/health`、macOS Codex 退出检测改为 `pgrep -x Codex`。 | 没有整 PR 合入，旧 renderer 改动未纳入。 |
| #30 优化删除确认与删除后页面稳定性 | 手工移植 | 删除确认改为按钮旁轻量确认；删除后隐藏/标记 React 管理的会话行而不是直接移除 DOM；本地 SQLite 删除时清理悬空 thread 引用。 | 已合入稳定基础。 |
| #54 重试次数和尝试次数控制 | 手工移植 | 设置面板新增 best-of 尝试次数、provider 请求/流式重试上限、固定 1 秒重试间隔控制。 | 已合入稳定基础；属于有风险但已通过本轮回归的功能。 |

## 本轮未合入

| PR | 当前处理 | 功能与用途 | 后续建议 |
|---|---|---|---|
| #91 自定义模型目录/白名单解锁 | 已从本地分支删除，未合入 `main` | 从环境变量或 `config.toml` 的 OpenAI-compatible provider `/v1/models` 拉取模型，并补进 Codex 模型选择列表。 | 后续如要继续合并，应从当前 `main` 新建独立分支重新处理，不和其他 PR 混在一个提交里；重点验证自定义 provider、代理、模型列表和 Statsig/React 状态 patch。 |
| #71 Context Guard handoff | 已从本地分支删除，未合入 `main` | 新增 `python -m codex_session_delete context-guard ...`，在长线程上下文爆满时生成本地 Markdown handoff，并包含实验性 steward/watch 流程。 | 后续如要继续合并，应从当前 `main` 新建独立分支重新处理；建议先合核心 CLI + handoff，再评估 steward UI，避免一次性引入过大变更。 |

## 明确没有整 PR 合入的内容

- #10 的旧 renderer 改动没有合入，只摘取 macOS/CLI 启动修复。
- #91 曾经做过独立分支验证，但按本轮决策删除分支，未进入 `main`。
- #71 曾经做过独立分支验证，但按本轮决策删除分支，未进入 `main`。
- 曾经存在的错误混合备份分支 `codex/mixed-pr-integration-backup` 已删除，避免保留包含 #91/#71 的混合引用。

## 当前本地分支状态

- `main`：已包含稳定基础修复提交 `afa8c72`。
- `codex/stable-pr-integration`：仍指向同一个稳定基础提交 `afa8c72`，可作为本轮稳定集成参考。
- #91 / #71 相关分支已删除。

## 后续继续合并建议

1. 优先保持 `main` 只包含已验证的稳定基础修复。
2. 如果继续合 #91，单独新建分支，例如 `codex/model-whitelist-unlock`，只处理模型白名单相关代码和测试。
3. 如果继续合 #71，单独新建分支，例如 `codex/context-guard-handoff`，先拆核心 handoff，再决定是否加入 steward/watch UI。
4. 每个 PR 分支独立跑针对性测试，验证通过后再决定是否合回 `main`。
5. 不再把 #91、#71 这类冲突密集 PR 和基础修复混在同一个提交里。

## 本轮已验证

- 稳定基础分支回归：`118 passed, 1 deselected`
- `main` 通过快进方式合入稳定基础提交。

