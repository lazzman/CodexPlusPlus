from __future__ import annotations

from pathlib import Path

import pytest

import codex_plus_gui as gui


def test_build_action_command_uses_existing_cli_commands():
    assert gui.build_action_command("setup", "python") == ["python", "-m", "codex_session_delete", "setup"]
    assert gui.build_action_command("remove", "python") == ["python", "-m", "codex_session_delete", "remove"]
    assert gui.build_action_command("remove_data", "python") == [
        "python",
        "-m",
        "codex_session_delete",
        "remove",
        "--remove-data",
    ]
    assert gui.build_action_command("check_update", "python") == ["python", "-m", "codex_session_delete", "check-update"]
    assert gui.build_action_command("update", "python") == ["python", "-m", "codex_session_delete", "update"]


def test_build_action_command_updates_source_with_git_rebase():
    assert gui.build_action_command("source_update", "python") == ["git", "pull", "--rebase"]


def test_build_action_command_covers_watcher_commands():
    assert gui.build_action_command("watch_install", "python") == ["python", "-m", "codex_session_delete", "watch-install"]
    assert gui.build_action_command("watch_remove", "python") == ["python", "-m", "codex_session_delete", "watch-remove"]
    assert gui.build_action_command("watch_enable", "python") == ["python", "-m", "codex_session_delete", "watch-enable"]
    assert gui.build_action_command("watch_disable", "python") == ["python", "-m", "codex_session_delete", "watch-disable"]


def test_build_action_command_rejects_unknown_action():
    with pytest.raises(ValueError, match="未知操作"):
        gui.build_action_command("missing", "python")


def test_build_launch_command_omits_empty_advanced_options():
    command = gui.build_launch_command(gui.LaunchOptions(), "python")

    assert command == ["python", "-m", "codex_session_delete", "launch"]


def test_build_launch_command_appends_filled_advanced_options():
    options = gui.LaunchOptions(
        app_dir="/Applications/OpenAI Codex.app",
        debug_port="9333",
        helper_port="58000",
        db="/tmp/state.sqlite",
        backup_dir="/tmp/backups",
    )

    command = gui.build_launch_command(options, "python")

    assert command == [
        "python",
        "-m",
        "codex_session_delete",
        "launch",
        "--app-dir",
        "/Applications/OpenAI Codex.app",
        "--db",
        "/tmp/state.sqlite",
        "--backup-dir",
        "/tmp/backups",
        "--debug-port",
        "9333",
        "--helper-port",
        "58000",
    ]


@pytest.mark.parametrize("value", ["abc", "0", "65536", "-1", "12.5"])
def test_validate_port_value_rejects_invalid_ports(value):
    with pytest.raises(ValueError, match="端口"):
        gui.validate_port_value("Debug 端口", value)


def test_validate_port_value_allows_blank_and_valid_ports():
    assert gui.validate_port_value("Debug 端口", "") == ""
    assert gui.validate_port_value("Debug 端口", "9229") == "9229"
    assert gui.validate_port_value("Debug 端口", " 57321 ") == "57321"


def test_watcher_supported_only_on_windows():
    assert gui.watcher_supported("win32") is True
    assert gui.watcher_supported("darwin") is False
    assert gui.watcher_supported("linux") is False
    assert gui.mac_watcher_supported("darwin") is True
    assert gui.mac_watcher_supported("win32") is False
    assert gui.mac_watcher_supported("linux") is False


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("就绪", "● 就绪"),
        ("正在执行操作...", "◌ 正在执行操作..."),
        ("Codex++ 启动中", "▶ Codex++ 启动中"),
        ("正在停止 Codex++", "◼ 正在停止 Codex++"),
        ("自定义状态", "• 自定义状态"),
    ],
)
def test_format_app_status_adds_badge_icons(status, expected):
    assert gui.format_app_status(status) == expected


@pytest.mark.parametrize(
    ("port", "listening", "expected"),
    [
        (9229, True, "● CDP 已监听 :9229"),
        (9229, False, "○ CDP 未监听 :9229"),
        (None, None, "⚠ CDP 端口无效"),
        (9333, None, "⚠ CDP 检测失败 :9333"),
    ],
)
def test_format_cdp_status_adds_badge_icons(port, listening, expected):
    assert gui.format_cdp_status(port, listening) == expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("macOS watcher 未开启", "○ macOS watcher 未开启"),
        ("macOS watcher 已开启", "● macOS watcher 已开启"),
        ("CDP 已监听，macOS watcher 空闲。", "● CDP 已监听，macOS watcher 空闲。"),
        ("发现原生 Codex 未开启 CDP，等待确认：[101]", "◌ 发现原生 Codex 未开启 CDP，等待确认：[101]"),
        ("未发现原生 Codex 进程，macOS watcher 空闲。", "○ 未发现原生 Codex 进程，macOS watcher 空闲。"),
        ("macOS watcher 接管失败，进入退避。", "⚠ macOS watcher 接管失败，进入退避。"),
        ("", "○ watcher 状态未知"),
    ],
)
def test_format_watcher_status_adds_badge_icons(status, expected):
    assert gui.format_watcher_status(status) == expected


@pytest.mark.parametrize(
    ("status", "expected_style"),
    [
        ("macOS watcher 未开启", "NeutralBadge.TLabel"),
        ("macOS watcher 已开启", "ReadyBadge.TLabel"),
        ("等待原生 Codex CDP grace period：[101]", "BusyBadge.TLabel"),
        ("未发现原生 Codex 进程，macOS watcher 空闲。", "NeutralBadge.TLabel"),
        ("macOS watcher 接管失败，进入退避。", "WarningBadge.TLabel"),
    ],
)
def test_watcher_status_badge_style_matches_state(status, expected_style):
    assert gui.watcher_status_badge_style(status) == expected_style


def test_gui_exposes_status_and_cdp_badges():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "app_status_badge_text" in text
    assert "cdp_status_text" in text
    assert "textvariable=self.app_status_badge_text" in text
    assert "textvariable=self.cdp_status_text" in text
    assert "def _set_status" in text
    assert "def _refresh_cdp_status" in text
    assert "CDP_STATUS_REFRESH_MS" in text
    assert "CDP_STATUS_TIMEOUT_SECONDS" in text
    assert "textvariable=self.status_text" not in text


def test_gui_buttons_clear_focus_after_click():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "def _make_button" in text
    assert 'kwargs.setdefault("takefocus", False)' in text
    assert 'kwargs.setdefault("style", "Codex.TButton")' in text
    assert 'button.state(["!focus"])' in text
    assert "self.root.after_idle(clear_focus)" in text
    assert "self.root.after(50, clear_focus)" in text
    assert 'button.bind("<FocusIn>"' in text
    assert 'button.bind("<ButtonRelease-1>"' in text
    assert "button = self._make_button(parent, text=label, command=command)" in text
    assert "self.ttk.Button(" in text
    assert text.count("self.ttk.Button(") == 1


def test_gui_log_text_hides_focus_without_blocking_selection_contract():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "def _configure_log_text" in text
    assert "self._configure_log_text()" in text
    assert "takefocus=0" in text
    assert "highlightthickness=0" in text
    assert "insertwidth=0" in text
    assert 'self.log_text.pack(fill="both", expand=True)\n        self._configure_log_text()' in text


def test_gui_buttons_use_central_enabled_state_helper():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "def _set_button_enabled" in text
    assert 'state="normal" if enabled else "disabled"' in text
    assert 'cursor="pointinghand" if enabled else "arrow"' in text
    assert 'style="Codex.TButton"' in text
    assert "style.map(" in text
    assert '("disabled", "#a8adb5")' in text
    assert "self._set_button_enabled(self.launch_button, not running)" in text
    assert "self._set_button_enabled(self.stop_button, running)" in text
    assert "self._set_button_enabled(self.mac_watcher_start_button, not running)" in text
    assert "self._set_button_enabled(self.mac_watcher_stop_button, running)" in text
    assert 'button.configure(state="disabled")' not in text
    assert 'self.launch_button.configure(state=' not in text
    assert 'self.stop_button.configure(state=' not in text


def test_non_windows_watcher_notice_uses_grid_layout_only():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert 'text="watcher 仅支持 Windows，当前平台不可用。").grid(' in text
    assert 'text="watcher 仅支持 Windows，当前平台不可用。").pack(' not in text
    assert "start_row=1" in text


def test_gui_exposes_macos_watcher_controls():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "开启 macOS watcher" in text
    assert "关闭 macOS watcher" in text
    assert "macOS watcher 只随当前 GUI 运行" in text
    assert "mac_watcher_badge_text" in text
    assert "format_watcher_status" in text
    assert "watcher_status_badge_style" in text
    assert "textvariable=self.mac_watcher_badge_text" in text
    assert "def _set_mac_watcher_status" in text
    assert "textvariable=self.mac_watcher_status" not in text


def test_gui_exposes_source_update_button():
    text = Path("codex_plus_gui.py").read_text(encoding="utf-8")

    assert "更新源码" in text
    assert 'self.run_task("source_update")' in text


def test_macos_codex_process_parser_excludes_codex_cli():
    output = "\n".join(
        [
            "101 /Applications/Codex.app/Contents/MacOS/Codex --original",
            "202 /usr/local/bin/codex --model gpt",
            "303 /Applications/OpenAI Codex.app/Contents/MacOS/Codex",
            "404 /Users/me/Applications/OpenAI.Codex.app/Contents/MacOS/Codex",
        ]
    )

    assert gui.parse_process_table(output, gui.is_macos_codex_app_command) == [101, 303, 404]


def test_launch_debug_port_uses_default_or_validated_value():
    assert gui.launch_debug_port(gui.LaunchOptions()) == 9229
    assert gui.launch_debug_port(gui.LaunchOptions(debug_port="9333")) == 9333
    with pytest.raises(ValueError, match="Debug 端口"):
        gui.launch_debug_port(gui.LaunchOptions(debug_port="bad"))


def test_mac_watcher_does_not_takeover_when_cdp_is_listening():
    events: list[str] = []

    watcher = gui.MacWatcher(
        gui.LaunchOptions(),
        gui.ManagedProcess(),
        output=events.append,
        status=events.append,
        launch_started=lambda: events.append("started"),
        launch_finished=lambda code: events.append(f"finished:{code}"),
        cdp_probe=lambda port: True,
        codex_finder=lambda: (_ for _ in ()).throw(AssertionError("不应查找进程")),
    )

    watcher.run_once()

    assert "CDP 已监听，macOS watcher 空闲。" in events
    assert "started" not in events


def test_mac_watcher_takes_over_after_grace_period_with_launch_options():
    now = [0.0]
    events: list[str] = []
    stopped_codex: list[list[int]] = []
    launched: list[list[str]] = []

    class FakeLaunchProcess:
        def is_running(self):
            return False

        def start(self, command, **kwargs):
            launched.append(command)

        def terminate(self):
            events.append("terminated")
            return True

    watcher = gui.MacWatcher(
        gui.LaunchOptions(app_dir="/Applications/OpenAI Codex.app", debug_port="9333", helper_port="58000"),
        FakeLaunchProcess(),
        output=events.append,
        status=events.append,
        launch_started=lambda: events.append("launch_started"),
        launch_finished=lambda code: events.append(f"finished:{code}"),
        grace_seconds=2.0,
        cdp_timeout_seconds=0.0,
        time_func=lambda: now[0],
        sleep_func=lambda seconds: None,
        cdp_probe=lambda port: False,
        codex_finder=lambda: [101],
        codex_stopper=lambda pids: stopped_codex.append(list(pids)),
        launcher_finder=lambda: [],
    )

    watcher.run_once()
    now[0] = 3.0
    watcher.run_once()

    assert stopped_codex == [[101]]
    assert launched == [[
        gui.sys.executable,
        "-m",
        "codex_session_delete",
        "launch",
        "--app-dir",
        "/Applications/OpenAI Codex.app",
        "--debug-port",
        "9333",
        "--helper-port",
        "58000",
    ]]
    assert "launch_started" in events
    assert "terminated" in events


def test_mac_watcher_backoff_prevents_repeated_failed_takeover():
    now = [0.0]
    starts = {"count": 0}

    class FakeLaunchProcess:
        def is_running(self):
            return False

        def start(self, command, **kwargs):
            starts["count"] += 1

        def terminate(self):
            return True

    watcher = gui.MacWatcher(
        gui.LaunchOptions(),
        FakeLaunchProcess(),
        output=lambda line: None,
        status=lambda text: None,
        launch_started=lambda: None,
        launch_finished=lambda code: None,
        grace_seconds=0.0,
        backoff_seconds=30.0,
        cdp_timeout_seconds=0.0,
        time_func=lambda: now[0],
        sleep_func=lambda seconds: None,
        cdp_probe=lambda port: False,
        codex_finder=lambda: [101],
        codex_stopper=lambda pids: None,
        launcher_finder=lambda: [],
    )

    watcher.run_once()
    watcher.run_once()
    watcher.run_once()

    assert starts["count"] == 1


def test_gui_close_stops_macos_watcher_before_destroying_window():
    app = gui.CodexPlusGuiApp.__new__(gui.CodexPlusGuiApp)
    events: list[str] = []

    class FakeLaunchProcess:
        def is_running(self):
            return False

    class FakeWatcher:
        def is_running(self):
            return True

        def stop(self):
            events.append("watcher_stopped")

    class FakeRoot:
        def destroy(self):
            events.append("destroyed")

    app.launch_process = FakeLaunchProcess()
    app.mac_watcher = FakeWatcher()
    app.root = FakeRoot()

    app.close()

    assert events == ["watcher_stopped", "destroyed"]


def test_managed_process_blocks_duplicate_start(monkeypatch, tmp_path):
    class FakeThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            pass

    class FakeProcess:
        stdout = []

        def poll(self):
            return None

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(gui.threading, "Thread", FakeThread)
    monkeypatch.setattr(gui.subprocess, "Popen", lambda *args, **kwargs: FakeProcess())
    process = gui.ManagedProcess()
    process.start(["python"], cwd=tmp_path, output=lambda line: None, finished=lambda code: None)

    with pytest.raises(RuntimeError, match="已在启动中"):
        process.start(["python"], cwd=tmp_path, output=lambda line: None, finished=lambda code: None)


def test_managed_process_terminate_current_process(monkeypatch):
    class FakeProcess:
        stdout = []

        def __init__(self):
            self.terminated = False

        def poll(self):
            return None if not self.terminated else 0

        def terminate(self):
            self.terminated = True

        def wait(self, timeout=None):
            return 0

    process = gui.ManagedProcess()
    process.process = FakeProcess()

    assert process.terminate() is True
    assert process.process.terminated is True


def test_start_gui_bat_bootstraps_venv_and_launches_gui():
    text = Path("start_gui.bat").read_text(encoding="utf-8")

    assert "python -m venv" in text
    assert "pip install -e ." in text
    assert "codex_plus_gui.py" in text
    assert "setup.bat" not in text


def test_start_gui_command_bootstraps_venv_and_launches_gui():
    text = Path("start_gui.command").read_text(encoding="utf-8")

    assert "Path(sys.argv[1]).expanduser().resolve()" in text
    assert 'PROJECT_ROOT=$(dirname "$SCRIPT_PATH")' in text
    assert 'cd "$PROJECT_ROOT"' in text
    assert 'VENV_DIR="$PROJECT_ROOT/.venv"' in text
    assert "python3 -m venv" in text
    assert "pip install -e ." in text
    assert '"$VENV_PY" "$PROJECT_ROOT/codex_plus_gui.py"' in text
    assert "请不要把 start_gui.command 复制到桌面" in text
    assert 'VENV_DIR="$PWD/.venv"' not in text
    assert '"$PWD/codex_plus_gui.py"' not in text
    assert "setup.bat" not in text
