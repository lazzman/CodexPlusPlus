# Codex++

<p align="center">
  <img src="docs/images/codex-plus-plus.png" alt="Codex++ icon" width="160">
</p>

<p align="center">
  <a href="README.md">中文</a> | English
</p>

<p align="center">
  <img alt="Release" src="https://img.shields.io/github/v/release/BigPizzaV3/CodexPlusPlus">
  <img alt="Stars" src="https://img.shields.io/github/stars/BigPizzaV3/CodexPlusPlus">
  <img alt="License" src="https://img.shields.io/github/license/BigPizzaV3/CodexPlusPlus">
  <img alt="Rust" src="https://img.shields.io/badge/rust-1.85%2B-orange">
  <img alt="Tauri" src="https://img.shields.io/badge/tauri-2.x-24C8DB">
</p>

Codex++ is an external enhancement launcher and manager for the Codex App. It does not modify the original Codex installation. Instead, it starts Codex externally and injects enhancements through the Chromium DevTools Protocol.

This repository is a personally maintained fork. Open upstream PRs are monitored alongside `origin/main`, suitable changes are reviewed manually, local `main` is rebased onto upstream, and updates are pushed only to `fork/main`, never to `origin`.

## Contents

- [Windows Usage](#windows-usage)
- [macOS Usage](#macos-usage)
- [Fork Maintenance](#fork-maintenance)
- [Highlights](#highlights)
- [User Script Migration Note](#user-script-migration-note)
- [Provider Sync](#provider-sync)
- [Common Commands](#common-commands)
- [FAQ](#faq)
- [Development](#development)
- [Feedback](#feedback)

## Windows Usage

Download the latest installer from [GitHub Releases](https://github.com/BigPizzaV3/CodexPlusPlus/releases):

- `CodexPlusPlus-*-windows-x64-setup.exe`

After installation, two entry points are available:

- `Codex++`: a silent launcher. It does not show the manager UI and only starts Codex with Codex++ injection.
- `Codex++ Manager`: a Tauri control panel for launch, diagnostics, repair, updates, relay injection, enhancements, and user scripts.

The Windows installer creates desktop and Start Menu shortcuts.

## macOS Usage

Download the matching DMG:

- Intel: `CodexPlusPlus-*-macos-x64.dmg`
- Apple Silicon: `CodexPlusPlus-*-macos-arm64.dmg`

Installation creates `/Applications/Codex++.app` and `/Applications/Codex++ 管理工具.app`.

## Fork Maintenance

- `origin` points to the upstream repository, and `fork` points to the personal fork.
- Open upstream PRs are monitored, summarized, and recorded, but they are not merged automatically.
- To sync upstream mainline changes, fetch remotes first, then rebase local `main` onto `origin/main`.
- Maintenance commits for this fork are pushed only to `fork/main`, never to `origin`.
- When upstream PRs are merged, partially picked, deferred, or rejected, update `docs/pr-integration-record.md` with the decision and reason.

## Highlights

- Adds a `Codex++` menu to manage enhancement features.
- Plugin entry unlock for API Key mode.
- Forced plugin install when the frontend blocks App unavailable states.
- Retry attempt controls that can raise best-of attempts and the active provider request and stream retry limits to 100.
- Session delete with confirmation and undo.
- Markdown export from local rollout files.
- Bulk Markdown ZIP export with per-session failure summaries.
- Project move for normal conversations and local projects.
- Bulk move with progress and failure records.
- Conversation Timeline with question markers, hover summaries, and quick jump.
- Provider Sync so historical conversations remain visible after you switch model_provider without losing historical conversations.
- Zed open entry detects remote SSH context and opens the matching remote file in Zed Remote Development from Codex.
- Windows shortcuts, uninstall entries, and GitHub Release updates.
- macOS `/Applications/Codex++.app` bundle generation.

In API Key mode, the native Codex plugin entry may require ChatGPT login and remain unavailable:

![Plugin entry unavailable in API Key mode](docs/images/pain-plugin-disabled.png)

The native Codex session list only has archive actions and no real delete button:

![Native session list lacks delete action](docs/images/pain-no-delete-button.png)

After launching through Codex++, the plugin entry is unlocked and a delete button appears when hovering a session:

![Codex++ unlocks plugin entry and adds delete button](docs/images/solution-plugin-and-delete.png)

The top bar shows `Codex++`, backend status, and the settings panel:

![Codex++ backend status indicator](docs/images/backend-status-indicator.png)
![Codex++ settings panel](docs/images/settings-panel.png)

Project charts:

![Contributors](https://contrib.rocks/image?repo=BigPizzaV3/CodexPlusPlus)
![Star History](https://api.star-history.com/svg?repos=BigPizzaV3/CodexPlusPlus&type=Date)

## User Script Migration Note

Earlier versions used local user scripts for retry controls, delete stability, plugin install click fallback, archive-page button styling, settings cleanup, and sidebar icon action buttons. These behaviors now live in the core `renderer-inject.js`.

If `~/.config/Codex++/user_scripts/` still contains old scripts such as `10-retry-attempt-controls.js` through `60-session-actions-icon-buttons.js`, disable or delete them after upgrading. Keeping them can cause duplicate patches, duplicate `MutationObserver` work, or duplicate style overrides. The user script system remains available for personal extensions.

## Provider Sync

When `Provider Sync` is enabled, Codex++ synchronizes local session metadata before launch so you can switch model_provider without losing historical conversations.

It aligns rollout files, SQLite thread records, and project path caches. It only fixes visibility metadata and does not rewrite message content. Busy files or SQLite locks are skipped so startup can continue.

## Common Commands

```bash
# Install dependencies
python -m pip install -e .

# Launch
python -m codex_session_delete launch

# Install shortcuts / app bundle
python -m codex_session_delete setup

# Remove
python -m codex_session_delete remove

# Remove logs and backup data too
python -m codex_session_delete remove --remove-data

# Check update / update
python -m codex_session_delete check-update
python -m codex_session_delete update

# Optional Windows watcher takeover
python -m codex_session_delete watch-install
python -m codex_session_delete watch-remove
python -m codex_session_delete watch-disable
python -m codex_session_delete watch-enable
```

Launch with a custom Codex path:

```bash
python -m codex_session_delete launch \
  --app-dir "C:/Program Files/WindowsApps/OpenAI.Codex_xxx/app" \
  --debug-port 9229 \
  --helper-port 57321
```

## FAQ

### The Codex++ menu does not appear

Make sure you launched from the `Codex++` shortcut instead of the original Codex entry. You can also inspect the Diagnostics and Logs pages in the manager.

### The plugin says the backend is disconnected

First test the helper endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:57321/backend/status -Body "{}" -ContentType "application/json"
```

If the endpoint works but the plugin still times out, it is usually a Codex page CDP bridge or script cache issue. Restart Codex++, or check manager logs for `renderer.script_loaded`, `bridge.request`, and `bridge.response`.

### macOS says the app cannot be opened or is damaged

Unsigned and unnotarized builds may be blocked by Gatekeeper. Allow the app in System Settings -> Privacy & Security. For formal distribution, configure Apple Developer ID signing and notarization.

### Does it support Intel Macs?

Yes. Releases provide both `macos-x64.dmg` and `macos-arm64.dmg`. Intel Macs should use the x64 package, while Apple Silicon Macs should use the arm64 package.

## Development

```bash
# Frontend checks
cd apps/codex-plus-manager
npm install
npm run check
npm run vite:build

# Rust checks
cd ../..
cargo fmt --check
cargo test
cargo build --release
```

Project structure:

```text
apps/
  codex-plus-launcher/          Silent launcher
  codex-plus-manager/           Tauri manager
assets/inject/
  renderer-inject.js            Enhancement script injected into Codex
crates/
  codex-plus-core/              Launch, injection, config, update, install, bridge
  codex-plus-data/              Session data, export, Provider Sync
scripts/installer/
  windows/CodexPlusPlus.nsi     Windows NSIS installer
  macos/package-dmg.sh          macOS DMG packager
```

The old Python entry points are no longer recommended. The remaining `codex_session_delete/` package is kept mainly for migration reference and historical compatibility.

## Feedback

Please use GitHub Issues for bug reports and feature requests:

<https://github.com/BigPizzaV3/CodexPlusPlus/issues>

## Friendly Links

- [LINUX DO](https://linux.do)

## Notes

Codex++ is an external enhancement tool and does not modify original Codex App files. If a future Codex App update changes page structure, the injection script may need updates.
