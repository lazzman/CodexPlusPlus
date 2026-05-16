# PR 集成记录

> 记录日期：2026-05-16
> 当前工作分支：`codex/absorb-pr-122-128`，在既有稳定基础上手工吸收远程 PR 核心稳定性逻辑。

本文档记录已进入稳定基线或当前集成分支的 PR、明确未合入的 PR，以及后续继续合并时的注意事项。

## Fork 同步维护策略

- 本仓库按个人 Fork 维护：`origin` 用于跟踪上游，`fork` 用于推送个人维护分支。
- 开放 PR 只做监控、汇总和风险评估，不自动合入当前分支。
- 合入上游主线前先同步 `origin/main`，本地 `main` 通过 rebase 跟进上游历史。
- 推送只面向 `fork/main`；不向 `origin` 推送维护提交。
- 任意 PR 的合入、部分摘取、暂缓或拒绝，都必须在本文档记录人工评估结论和验证结果。

## 已合入稳定基线或当前分支

| PR | 合入方式 | 功能与用途 | 备注 |
|---|---|---|---|
| #60 fix API Key 自定义 model_provider | 完整合入 | 修复 API Key 模式下自定义 provider / 中转端点被插件解锁逻辑误改为 `chatgpt`，导致 API Key 不发送的问题；同时保留自定义 `base_url` 主机加入 `NO_PROXY` 的逻辑。 | 属于稳定基础修复；当前分支补充 `CODEX_HOME` 下的 provider 配置读取。 |
| #82 本地代理注入改为显式开启 | 手工整合 | 新增 `launch --proxy`；默认不再自动探测并注入本地代理，只有显式传参时才注入代理环境变量。 | 已和 #60 的 `NO_PROXY` 策略合并：默认不注入代理，但仍为自定义 provider 主机补 `NO_PROXY`。 |
| #10 macOS 二次打开不响应修复 | 部分摘取 | 摘取 macOS/CLI 相关修复：`.app` launcher 后台启动、helper 端口占用时检查 `/health`、macOS Codex 退出检测改为 `pgrep -x Codex`。 | 没有整 PR 合入，旧 renderer 改动未纳入。 |
| #30 优化删除确认与删除后页面稳定性 | 手工移植 | 删除确认改为按钮旁轻量确认；删除后隐藏/标记 React 管理的会话行而不是直接移除 DOM；本地 SQLite 删除时清理悬空 thread 引用。 | 已合入稳定基础。 |
| #54 重试次数和尝试次数控制 | 手工移植 | 设置面板新增 best-of 尝试次数、provider 请求/流式重试上限、固定 1 秒重试间隔控制。 | 已合入稳定基础；属于有风险但已通过本轮回归的功能。 |
| #104 CODEX_HOME 数据库路径 | 手工移植 | `launch --db` 默认值改为读取 `CODEX_HOME/state_5.sqlite`，避免多 profile 串用默认 `~/.codex/state_5.sqlite`。 | 同步补充 renderer 对失效投影会话的清理逻辑。 |
| #109 插件入口解锁时序修复 | 手工移植 | 插件入口不再在扫描阶段提前污染模型选择上下文，改为捕获阶段按需切换 `authMethod`。 | 保留 #60 的自定义 provider / `NO_PROXY` 兼容逻辑。 |
| #113 多 Codex 窗口注入 | 手工移植 | CDP 注入改为追踪多个 Codex page target，用户脚本重载会覆盖所有仍可用 target。 | 新增前台恢复扫描，减少新窗口/恢复前台漏注入。 |
| #114 bridge 修复与 HTTP fallback | 手工移植 | bridge 增加超时、错误日志、后端状态/修复接口和 backend status HTTP fallback。 | 不开放删除/撤销 HTTP mutation；只为后端状态/修复提供 fallback。 |
| #105 helper/bridge 稳定性 | 手工移植 | 健康 helper 复用、bridge watchdog、运行日志追加、CDP 优先存活判断。 | macOS 存活检测保持当前规范的 `pgrep -x Codex` 兜底。 |
| #112 批量 Markdown ZIP 导出 | 手工移植 | 后端新增 `BulkExportResult`、`export_zip` 和 `/export-markdown-zip`，前端支持多选导出 ZIP 与失败摘要。 | 未新增运行时依赖，使用标准库 `zipfile`。 |
| #115 批量移动 | 手工移植 | 后端新增 `/move-thread-projectless` 并清空 SQLite/rollout `cwd`，前端支持批量选择、进度和失败记录。 | 保持现有单条项目移动投影与排序修正逻辑。 |
| #122 CDP 多页面注入资源释放 | 手工摘取核心稳定性逻辑 | `MultiPageInjection.close()` 统一停止 watcher、关闭 bridge socket 并等待 watcher 线程；`/json` target 查询释放 requests session；helper shutdown 会关闭注入 manager。 | 未直接 merge PR；只吸收资源释放和安静退出相关逻辑，并保留当前批量导出、批量移动、用户脚本和 Provider 同步实现。 |
| #128 bridge watchdog 与手动修复稳定性 | 手工摘取核心稳定性逻辑 | `evaluate_script()` 支持 `await_promise`/`timeout`；bridge 重入保留 pending callbacks；watchdog 执行真实 `/backend/status` roundtrip；renderer 后端状态使用 runtime/request id 防旧响应覆盖，手动修复失败后尝试底层 `codexSessionDeleteV2` binding fallback。 | 未吸收 #128 的图片、推荐内容或广告相关变更；helper mutation 安全边界保持不变。 |

## 本轮未合入

| PR | 当前处理 | 功能与用途 | 后续建议 |
|---|---|---|---|
| #91 自定义模型目录/白名单解锁 | 已从本地分支删除，未合入 `main` | 从环境变量或 `config.toml` 的 OpenAI-compatible provider `/v1/models` 拉取模型，并补进 Codex 模型选择列表。 | 后续如要继续合并，应从当前 `main` 新建独立分支重新处理，不和其他 PR 混在一个提交里；重点验证自定义 provider、代理、模型列表和 Statsig/React 状态 patch。 |
| #71 Context Guard handoff | 已从本地分支删除，未合入 `main` | 新增 `python -m codex_session_delete context-guard ...`，在长线程上下文爆满时生成本地 Markdown handoff，并包含实验性 steward/watch 流程。 | 后续如要继续合并，应从当前 `main` 新建独立分支重新处理；建议先合核心 CLI + handoff，再评估 steward UI，避免一次性引入过大变更。 |
| #103 Electron fuse patch | 暂缓，未合入 | 通过修改本机 Electron fuse 解除限制。 | 高风险本机二进制 patch，不作为默认能力吸收。 |
| #110 / #82 代理相关扩展 | #82 已在基线；#110 未单独吸收 | 启动代理策略。 | 当前保持 `--proxy` 显式开启契约，不引入额外默认代理行为。 |
| #30 / #10 / #54 | 已在基线中记录，不在本轮重复整合 | 删除确认、macOS/helper 稳定基础、重试控制。 | 本轮不回退既有基线改动。 |

## 明确没有整 PR 合入的内容

- #10 的旧 renderer 改动没有合入，只摘取 macOS/CLI 启动修复。
- #103 Electron fuse 二进制 patch 没有实现，避免默认修改用户本机应用二进制。
- #60 只确认并保留自定义 provider `base_url` 主机加入 `NO_PROXY` 的低风险逻辑，没有回退 #109 renderer 时序修复。
- #54/#91/#71/#30/#10 本轮未重新整 PR 合并；其中 #54/#30/#10 的稳定基础已存在于当前基线。
- #91 曾经做过独立分支验证，但按本轮决策删除分支，未进入 `main`。
- #71 曾经做过独立分支验证，但按本轮决策删除分支，未进入 `main`。
- #128 的图片、群二维码、推荐内容和广告/赞助 UI 相关变更没有合入；当前仍保持无广告/无推荐内容的 renderer 契约。
- 曾经存在的错误混合备份分支 `codex/mixed-pr-integration-backup` 已删除，避免保留包含 #91/#71 的混合引用。

## 当前本地分支状态

- `codex/absorb-pr-122-128`：当前实现分支，在 #104/#109/#113/#114/#105/#112/#115 稳定基础上手工吸收 #122/#128 的核心稳定性逻辑。
- `codex/absorb-remote-pr-features`：旧实现分支，手工吸收 #104/#109/#113/#114/#105/#112/#115。
- `main`：已包含稳定基础修复提交 `afa8c72`。
- `codex/stable-pr-integration`：仍指向同一个稳定基础提交 `afa8c72`，可作为稳定集成参考。
- #91 / #71 相关分支已删除。

## 后续继续合并建议

1. 优先保持 `main` 只包含已验证的稳定基础修复。
2. 如果继续合 #91，单独新建分支，例如 `codex/model-whitelist-unlock`，只处理模型白名单相关代码和测试。
3. 如果继续合 #71，单独新建分支，例如 `codex/context-guard-handoff`，先拆核心 handoff，再决定是否加入 steward/watch UI。
4. 每个 PR 分支独立跑针对性测试，验证通过后再决定是否合回 `main`。
5. 不再把 #91、#71 这类冲突密集 PR 和基础修复混在同一个提交里。

## 本轮已验证

- 稳定基础分支回归：`118 passed, 1 deselected`。
- 2026-05-16 吸收 #122/#128 后验证：
  - `.venv/bin/python -m pytest tests/test_cdp.py tests/test_launcher_cli.py tests/test_renderer_script.py tests/test_helper_server.py -q` 未运行成功：当前 `.venv` 缺少 `pytest`。
  - `python3 -m pytest tests/test_cdp.py tests/test_launcher_cli.py tests/test_renderer_script.py tests/test_helper_server.py -q`：`125 passed`。
  - `python3 -m pytest -q`：`301 passed`。
  - `node --check codex_session_delete/inject/renderer-inject.js`：通过。
  - `git diff --check`：通过。
