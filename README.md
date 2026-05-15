# Codex++

<p align="center">
  <img src="docs/images/codex-plus-plus.png" alt="Codex++ 图标" width="160">
</p>

<p align="center">
  中文 | <a href="README_EN.md">English</a>
</p>

<p align="center">
  <img alt="Release" src="https://img.shields.io/github/v/release/BigPizzaV3/CodexPlusPlus">
  <img alt="Stars" src="https://img.shields.io/github/stars/BigPizzaV3/CodexPlusPlus">
  <img alt="License" src="https://img.shields.io/github/license/BigPizzaV3/CodexPlusPlus">
  <img alt="Rust" src="https://img.shields.io/badge/rust-1.85%2B-orange">
  <img alt="Tauri" src="https://img.shields.io/badge/tauri-2.x-24C8DB">
</p>

Codex++ 是面向 Codex App 的外部增强启动器和管理工具。它不修改 Codex App 原始安装文件，而是通过外部 launcher 启动 Codex，并使用 Chromium DevTools Protocol 注入增强脚本。

本仓库是个人 Fork 的同步维护版本。维护目标是监控 `origin` 的开放 PR 和 `origin/main`，人工评估后把适合本 Fork 的改动 rebase 到本地 `main`，并只推送到 `fork/main`，不推送到 `origin`。

## 目录

- [Windows 使用](#windows-使用)
- [macOS 使用](#macos-使用)
- [Fork 维护策略](#fork-维护策略)
- [功能亮点](#功能亮点)
- [用户脚本迁移提示](#用户脚本迁移提示)
- [Provider 同步](#provider-同步)
- [常用命令](#常用命令)
- [常见问题](#常见问题)
- [开发](#开发)
- [反馈](#反馈)

## Windows 使用

从 [GitHub Releases](https://github.com/BigPizzaV3/CodexPlusPlus/releases) 下载最新版安装包：

- `CodexPlusPlus-*-windows-x64-setup.exe`

安装后会有两个入口：

- `Codex++`：静默启动入口，不显示管理界面，只负责启动 Codex 并注入增强功能。
- `Codex++ 管理工具`：Tauri 控制面板，用于启动、检查、修复、更新、配置中转注入、管理增强功能和用户脚本。

Windows 安装包会创建桌面和开始菜单快捷方式。

## macOS 使用

下载适合架构的 DMG：

- Intel：`CodexPlusPlus-*-macos-x64.dmg`
- Apple Silicon：`CodexPlusPlus-*-macos-arm64.dmg`

安装后会生成 `/Applications/Codex++.app` 和 `/Applications/Codex++ 管理工具.app`。

## Fork 维护策略

- 上游仓库使用 `origin`，个人 Fork 使用 `fork`。
- 日常同步先监控 `origin` 的开放 PR 和 `origin/main`，只做汇总、评估和记录，不自动合入开放 PR。
- 需要同步上游主线时，先抓取远端，再把本地 `main` rebase 到 `origin/main`。
- 本 Fork 的维护提交只推送到 `fork/main`，不推送到 `origin`。
- 合入或放弃上游 PR 时，同步维护 `docs/pr-integration-record.md`，说明已合入、部分摘取、暂缓或未合入原因。

## 功能亮点

- 顶部 `Codex++` 菜单：集中管理增强功能。
- 插件入口解锁：API Key 模式下显示并启用插件入口。
- 特殊插件强制安装：解除 App unavailable / 应用不可用导致的前端安装禁用。
- 重试次数控制：可选把 best-of 尝试数和当前 provider 请求/流式重试上限提升到 100。
- 会话删除：悬停显示删除按钮，删除前确认并支持撤销。
- Markdown 导出：按本地 rollout 导出带时间戳的会话 Markdown。
- 批量导出 ZIP：多选会话后一次导出 Markdown ZIP，并记录失败摘要。
- 会话项目移动：把会话移动到普通对话或其他本地项目。
- 批量移动：多选会话后移动到普通对话或本地项目，并显示进度和失败记录。
- 对话 Timeline：右侧显示用户提问时间线，悬停摘要，点击跳转。
- Provider 同步：切换 model_provider 或供应商时不丢历史会话。
- Windows 快捷方式、卸载项、GitHub Release 更新。
- macOS `/Applications/Codex++.app` 生成。

API Key 登录模式下，Codex 原生插件入口会提示需要登录 ChatGPT，导致插件功能无法正常使用：

![API Key 模式下插件入口不可用](docs/images/pain-plugin-disabled.png)

Codex 原生会话列表只有归档入口，没有真正的删除按钮：

![原生会话列表缺少删除能力](docs/images/pain-no-delete-button.png)

Codex++ 启动后会解锁插件入口，并在会话列表悬停时显示删除按钮：

![Codex++ 解锁插件入口并添加删除按钮](docs/images/solution-plugin-and-delete.png)

顶部菜单栏会出现 `Codex++`，可以查看后端状态并打开设置面板：

![Codex++ 后端状态指示灯](docs/images/backend-status-indicator.png)
![Codex++ 设置面板](docs/images/settings-panel.png)

项目图表：

![Contributors](https://contrib.rocks/image?repo=BigPizzaV3/CodexPlusPlus)
![Star History](https://api.star-history.com/svg?repos=BigPizzaV3/CodexPlusPlus&type=Date)

## 用户脚本迁移提示

早期版本依赖本机用户脚本提供重试控制、删除稳定性、插件安装点击兜底、归档页按钮样式、设置页清理和侧边栏图标按钮。升级到当前版本后，这些能力已迁入核心 `renderer-inject.js`。

如果你的 `~/.config/Codex++/user_scripts/` 中仍有旧脚本，例如 `10-retry-attempt-controls.js` 到 `60-session-actions-icon-buttons.js`，建议禁用或删除它们，避免重复 patch、重复 `MutationObserver` 或重复样式覆盖。用户脚本系统仍保留给个人扩展使用。

## Provider 同步

启用 `Provider 同步` 后，Codex++ 会在启动前同步本地会话 metadata，让切换 model_provider 或供应商时不丢历史会话。

同步范围包括 rollout 文件、SQLite 线程记录和项目路径缓存；只修复会话可见性 metadata，不改写消息内容。遇到文件锁或 SQLite 忙碌时会跳过并继续启动。

## 常用命令

```bash
# 安装依赖
python -m pip install -e .

# 启动
python -m codex_session_delete launch

# 安装快捷方式 / app bundle
python -m codex_session_delete setup

# 卸载
python -m codex_session_delete remove

# 同时删除日志和备份
python -m codex_session_delete remove --remove-data

# 检查更新 / 更新
python -m codex_session_delete check-update
python -m codex_session_delete update

# Windows watcher 自动接管
python -m codex_session_delete watch-install
python -m codex_session_delete watch-remove
python -m codex_session_delete watch-disable
python -m codex_session_delete watch-enable
```

直接指定 Codex 安装目录：

```bash
python -m codex_session_delete launch \
  --app-dir "C:/Program Files/WindowsApps/OpenAI.Codex_xxx/app" \
  --debug-port 9229 \
  --helper-port 57321
```

## 常见问题

### Codex++ 菜单没出现

确认是从 `Codex++` 入口启动，而不是原版 Codex。也可以打开管理工具的“诊断”和“日志”页面查看注入状态。

### 插件内显示后端连不上

先在浏览器或 PowerShell 里测试：

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:57321/backend/status -Body "{}" -ContentType "application/json"
```

如果接口正常，但插件仍显示超时，通常是 Codex 页面里的 CDP bridge 或脚本缓存问题。重启 Codex++，或在管理工具里查看日志中的 `renderer.script_loaded`、`bridge.request`、`bridge.response`。

### macOS 提示无法打开或已损坏

当前安装包未签名或未公证时，macOS Gatekeeper 可能拦截。可以在“系统设置 - 隐私与安全性”中允许打开。正式分发建议配置 Apple Developer ID 签名和 notarization。

### macOS Intel 能用吗

可以。Release 会分别提供 `macos-x64.dmg` 和 `macos-arm64.dmg`。Intel Mac 下载 x64 包，Apple Silicon 下载 arm64 包。

## 开发

```bash
# 前端检查
cd apps/codex-plus-manager
npm install
npm run check
npm run vite:build

# Rust 检查
cd ../..
cargo fmt --check
cargo test
cargo build --release
```

主要结构：

```text
apps/
  codex-plus-launcher/          静默启动入口
  codex-plus-manager/           Tauri 管理工具
assets/inject/
  renderer-inject.js            注入到 Codex 渲染端的增强脚本
crates/
  codex-plus-core/              启动、注入、配置、更新、安装、桥接等核心逻辑
  codex-plus-data/              会话数据、导出、Provider 同步
scripts/installer/
  windows/CodexPlusPlus.nsi     Windows NSIS 安装包
  macos/package-dmg.sh          macOS DMG 打包
```

不建议继续使用旧 Python 入口；仓库中保留的 `codex_session_delete/` 主要用于迁移参考和兼容历史代码。

## 反馈

问题反馈和功能建议请使用 GitHub Issues：

<https://github.com/BigPizzaV3/CodexPlusPlus/issues>

## 友情链接

- [LINUX DO](https://linux.do)

## 说明

Codex++ 是外部增强工具，不修改 Codex App 原始文件。Codex App 更新后，如果页面结构变化，可能需要更新注入脚本。
