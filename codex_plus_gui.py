from __future__ import annotations

import queue
import os
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DEBUG_PORT = 9229
CDP_STATUS_REFRESH_MS = 2000
CDP_STATUS_TIMEOUT_SECONDS = 0.2
MAC_WATCHER_INTERVAL_SECONDS = 3.0
MAC_WATCHER_GRACE_SECONDS = 2.0
MAC_WATCHER_BACKOFF_SECONDS = 30.0
MAC_WATCHER_CDP_TIMEOUT_SECONDS = 25.0


@dataclass(frozen=True)
class LaunchOptions:
    app_dir: str = ""
    debug_port: str = ""
    helper_port: str = ""
    db: str = ""
    backup_dir: str = ""


def normalized_value(value: str | None) -> str:
    return (value or "").strip()


def validate_port_value(label: str, value: str | None) -> str:
    cleaned = normalized_value(value)
    if not cleaned:
        return ""
    if not cleaned.isdecimal():
        raise ValueError(f"{label} 必须是 1 到 65535 之间的数字。")
    port = int(cleaned)
    if port < 1 or port > 65535:
        raise ValueError(f"{label} 必须是 1 到 65535 之间的数字。")
    return cleaned


def base_module_command(python_executable: str | None = None) -> list[str]:
    return [python_executable or sys.executable, "-m", "codex_session_delete"]


def build_cli_command(command: str, extra_args: Iterable[str] = (), python_executable: str | None = None) -> list[str]:
    return [*base_module_command(python_executable), command, *extra_args]


def build_launch_command(options: LaunchOptions, python_executable: str | None = None) -> list[str]:
    args: list[str] = []
    app_dir = normalized_value(options.app_dir)
    db = normalized_value(options.db)
    backup_dir = normalized_value(options.backup_dir)
    debug_port = validate_port_value("Debug 端口", options.debug_port)
    helper_port = validate_port_value("Helper 端口", options.helper_port)

    if app_dir:
        args.extend(["--app-dir", app_dir])
    if db:
        args.extend(["--db", db])
    if backup_dir:
        args.extend(["--backup-dir", backup_dir])
    if debug_port:
        args.extend(["--debug-port", debug_port])
    if helper_port:
        args.extend(["--helper-port", helper_port])
    return build_cli_command("launch", args, python_executable)


def launch_debug_port(options: LaunchOptions) -> int:
    value = validate_port_value("Debug 端口", options.debug_port)
    return int(value) if value else DEFAULT_DEBUG_PORT


def build_action_command(action: str, python_executable: str | None = None) -> list[str]:
    if action == "source_update":
        return ["git", "pull", "--rebase"]

    mapping: dict[str, tuple[str, list[str]]] = {
        "setup": ("setup", []),
        "remove": ("remove", []),
        "remove_data": ("remove", ["--remove-data"]),
        "check_update": ("check-update", []),
        "update": ("update", []),
        "watch_install": ("watch-install", []),
        "watch_remove": ("watch-remove", []),
        "watch_enable": ("watch-enable", []),
        "watch_disable": ("watch-disable", []),
    }
    if action not in mapping:
        raise ValueError(f"未知操作：{action}")
    command, args = mapping[action]
    return build_cli_command(command, args, python_executable)


def watcher_supported(platform: str | None = None) -> bool:
    return (platform or sys.platform) == "win32"


def mac_watcher_supported(platform: str | None = None) -> bool:
    return (platform or sys.platform) == "darwin"


def cdp_listening(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def format_app_status(status: str) -> str:
    mapping = {
        "就绪": "● 就绪",
        "正在执行操作...": "◌ 正在执行操作...",
        "Codex++ 启动中": "▶ Codex++ 启动中",
        "正在停止 Codex++": "◼ 正在停止 Codex++",
    }
    cleaned = normalized_value(status)
    return mapping.get(cleaned, f"• {cleaned or '未知状态'}")


def app_status_badge_style(status: str) -> str:
    mapping = {
        "就绪": "ReadyBadge.TLabel",
        "正在执行操作...": "BusyBadge.TLabel",
        "Codex++ 启动中": "RunningBadge.TLabel",
        "正在停止 Codex++": "StoppingBadge.TLabel",
    }
    return mapping.get(normalized_value(status), "NeutralBadge.TLabel")


def format_cdp_status(port: int | None, listening: bool | None) -> str:
    if port is None:
        return "⚠ CDP 端口无效"
    if listening is True:
        return f"● CDP 已监听 :{port}"
    if listening is False:
        return f"○ CDP 未监听 :{port}"
    return f"⚠ CDP 检测失败 :{port}"


def cdp_status_badge_style(listening: bool | None) -> str:
    if listening is True:
        return "ReadyBadge.TLabel"
    if listening is False:
        return "NeutralBadge.TLabel"
    return "WarningBadge.TLabel"


def format_watcher_status(status: str) -> str:
    cleaned = normalized_value(status)
    if not cleaned:
        return "○ watcher 状态未知"
    if any(keyword in cleaned for keyword in ("失败", "退避", "运行失败")):
        return f"⚠ {cleaned}"
    if any(keyword in cleaned for keyword in ("已开启", "CDP 已监听", "接管成功")):
        return f"● {cleaned}"
    if any(keyword in cleaned for keyword in ("等待", "开始接管")) or ("发现" in cleaned and "未发现" not in cleaned):
        return f"◌ {cleaned}"
    if any(keyword in cleaned for keyword in ("未开启", "已关闭", "空闲", "未发现")):
        return f"○ {cleaned}"
    return f"• {cleaned}"


def watcher_status_badge_style(status: str) -> str:
    cleaned = normalized_value(status)
    if any(keyword in cleaned for keyword in ("失败", "退避", "运行失败")):
        return "WarningBadge.TLabel"
    if any(keyword in cleaned for keyword in ("已开启", "CDP 已监听", "接管成功")):
        return "ReadyBadge.TLabel"
    if any(keyword in cleaned for keyword in ("等待", "开始接管")) or ("发现" in cleaned and "未发现" not in cleaned):
        return "BusyBadge.TLabel"
    return "NeutralBadge.TLabel"


def is_macos_codex_app_command(command: str) -> bool:
    return any(
        marker in command
        for marker in (
            "/Codex.app/Contents/MacOS/Codex",
            "/OpenAI Codex.app/Contents/MacOS/Codex",
            "/OpenAI.Codex.app/Contents/MacOS/Codex",
        )
    )


def parse_process_table(output: str, predicate: Callable[[str], bool]) -> list[int]:
    pids: list[int] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        if predicate(parts[1]):
            pids.append(int(parts[0]))
    return pids


def find_macos_codex_processes() -> list[int]:
    result = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True, check=False)
    return parse_process_table(result.stdout, is_macos_codex_app_command)


def find_macos_launcher_processes() -> list[int]:
    result = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True, check=False)
    current_pid = os.getpid()
    return [
        pid
        for pid in parse_process_table(result.stdout, lambda command: "-m codex_session_delete launch" in command)
        if pid != current_pid
    ]


def stop_processes(pids: list[int]) -> None:
    if pids:
        subprocess.run(["kill", "-TERM", *[str(pid) for pid in pids]], check=False)


class MacWatcher:
    def __init__(
        self,
        options: LaunchOptions,
        launch_process: "ManagedProcess",
        *,
        output: Callable[[str], None],
        status: Callable[[str], None],
        launch_started: Callable[[], None],
        launch_finished: Callable[[int], None],
        interval: float = MAC_WATCHER_INTERVAL_SECONDS,
        grace_seconds: float = MAC_WATCHER_GRACE_SECONDS,
        backoff_seconds: float = MAC_WATCHER_BACKOFF_SECONDS,
        cdp_timeout_seconds: float = MAC_WATCHER_CDP_TIMEOUT_SECONDS,
        time_func: Callable[[], float] = time.time,
        sleep_func: Callable[[float], None] = time.sleep,
        cdp_probe: Callable[[int], bool] = cdp_listening,
        codex_finder: Callable[[], list[int]] = find_macos_codex_processes,
        codex_stopper: Callable[[list[int]], None] = stop_processes,
        launcher_finder: Callable[[], list[int]] = find_macos_launcher_processes,
        launcher_stopper: Callable[[list[int]], None] = stop_processes,
    ) -> None:
        self.options = options
        self.launch_process = launch_process
        self.output = output
        self.status = status
        self.launch_started = launch_started
        self.launch_finished = launch_finished
        self.interval = interval
        self.grace_seconds = grace_seconds
        self.backoff_seconds = backoff_seconds
        self.cdp_timeout_seconds = cdp_timeout_seconds
        self.time_func = time_func
        self.sleep_func = sleep_func
        self.cdp_probe = cdp_probe
        self.codex_finder = codex_finder
        self.codex_stopper = codex_stopper
        self.launcher_finder = launcher_finder
        self.launcher_stopper = launcher_stopper
        self.debug_port = launch_debug_port(options)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_state: str | None = None
        self._candidate_pids: tuple[int, ...] | None = None
        self._candidate_since = 0.0
        self._backoff_until = 0.0

    def start(self) -> None:
        if self.is_running():
            raise RuntimeError("macOS watcher 已在运行。")
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.status("macOS watcher 已开启")
        self.output("macOS watcher 已开启。")

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None and threading.current_thread() is not self._thread:
            self._thread.join(timeout=2)
        self.status("macOS watcher 已关闭")
        self.output("macOS watcher 已关闭。")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def run_once(self) -> None:
        if self.cdp_probe(self.debug_port):
            self._candidate_pids = None
            self._set_state("cdp_ok", "CDP 已监听，macOS watcher 空闲。")
            return

        pids = self.codex_finder()
        if not pids:
            self._candidate_pids = None
            self._set_state("idle", "未发现原生 Codex 进程，macOS watcher 空闲。")
            return

        now = self.time_func()
        if now < self._backoff_until:
            self._set_state("backoff", f"接管失败后退避中，剩余 {self._backoff_until - now:.1f} 秒。")
            return

        candidate = tuple(sorted(pids))
        if self._candidate_pids != candidate:
            self._candidate_pids = candidate
            self._candidate_since = now
            self._set_state("grace", f"发现原生 Codex 未开启 CDP，等待确认：{list(candidate)}")
            return

        if now - self._candidate_since < self.grace_seconds:
            self._set_state("grace", f"等待原生 Codex CDP grace period：{list(candidate)}")
            return

        self._set_state("takeover", f"开始接管原生 Codex：{list(candidate)}")
        self._candidate_pids = None
        if self.takeover():
            self._set_state("cdp_ok", "macOS watcher 接管成功。")
        else:
            self._backoff_until = self.time_func() + self.backoff_seconds
            self._set_state("failed", "macOS watcher 接管失败，进入退避。")

    def takeover(self) -> bool:
        if self.cdp_probe(self.debug_port):
            return True

        launcher_pids = self.launcher_finder()
        if launcher_pids:
            self.output(f"停止旧 Codex++ 启动进程：{launcher_pids}")
            self.launcher_stopper(launcher_pids)

        codex_pids = self.codex_finder()
        if codex_pids:
            self.output(f"停止原生 Codex 进程：{codex_pids}")
            self.codex_stopper(codex_pids)
            self.sleep_func(1.0)

        if self.launch_process.is_running():
            self.output("Codex++ 启动进程已经在运行，跳过重复接管。")
            return False

        command = build_launch_command(self.options)
        self.output("$ " + " ".join(command))
        try:
            self.launch_process.start(
                command,
                cwd=PROJECT_ROOT,
                output=self.output,
                finished=self.launch_finished,
            )
        except Exception as exc:
            self.output(f"启动 Codex++ 失败：{exc}")
            return False
        self.launch_started()
        if self._wait_for_cdp():
            return True
        self.output("等待 CDP 超时，停止本次接管启动进程。")
        self.launch_process.terminate()
        return False

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception as exc:
                self.output(f"macOS watcher 运行失败：{exc}")
                self._backoff_until = self.time_func() + self.backoff_seconds
            self._stop.wait(self.interval)

    def _wait_for_cdp(self) -> bool:
        deadline = self.time_func() + self.cdp_timeout_seconds
        while self.time_func() < deadline and not self._stop.is_set():
            if self.cdp_probe(self.debug_port):
                return True
            self.sleep_func(0.5)
        return False

    def _set_state(self, state: str, message: str) -> None:
        if self._last_state != state:
            self.output(message)
            self.status(message)
        self._last_state = state


class ManagedProcess:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None
        self._waiter: threading.Thread | None = None

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def start(
        self,
        command: list[str],
        *,
        cwd: Path,
        output: Callable[[str], None],
        finished: Callable[[int], None],
    ) -> None:
        if self.is_running():
            raise RuntimeError("Codex++ 已在启动中，请先停止当前进程。")

        self.process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._read_output, args=(output,), daemon=True)
        self._reader.start()
        self._waiter = threading.Thread(target=self._wait_for_exit, args=(finished,), daemon=True)
        self._waiter.start()

    def terminate(self) -> bool:
        if not self.is_running() or self.process is None:
            return False
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        return True

    def _read_output(self, output: Callable[[str], None]) -> None:
        process = self.process
        if process is None or process.stdout is None:
            return
        for line in process.stdout:
            output(line.rstrip("\n"))

    def _wait_for_exit(self, finished: Callable[[int], None]) -> None:
        process = self.process
        if process is None:
            return
        return_code = process.wait()
        finished(return_code)


def _import_tkinter():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    return tk, ttk, filedialog, messagebox, scrolledtext


class CodexPlusGuiApp:
    def __init__(self, root) -> None:
        tk, ttk, filedialog, messagebox, scrolledtext = _import_tkinter()
        self.tk = tk
        self.ttk = ttk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.scrolledtext = scrolledtext
        self.root = root
        self.output_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.launch_process = ManagedProcess()
        self.task_process = ManagedProcess()
        self.mac_watcher: MacWatcher | None = None
        self.advanced_visible = tk.BooleanVar(value=False)
        self.status_text = tk.StringVar(value="就绪")
        self.app_status_badge_text = tk.StringVar(value=format_app_status("就绪"))
        self.cdp_status_text = tk.StringVar(value=format_cdp_status(DEFAULT_DEBUG_PORT, False))
        self.mac_watcher_status = tk.StringVar(value="macOS watcher 未开启")
        self.mac_watcher_badge_text = tk.StringVar(value=format_watcher_status("macOS watcher 未开启"))
        self.app_dir = tk.StringVar()
        self.debug_port = tk.StringVar()
        self.helper_port = tk.StringVar()
        self.db = tk.StringVar()
        self.backup_dir = tk.StringVar()
        self.launch_button = None
        self.stop_button = None
        self.mac_watcher_start_button = None
        self.mac_watcher_stop_button = None
        self.app_status_badge_label = None
        self.cdp_status_label = None
        self.mac_watcher_status_label = None
        self.advanced_frame = None
        self.log_text = None
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self._drain_output_queue)
        self.root.after(0, self._refresh_cdp_status)

    def _build(self) -> None:
        self.root.title("Codex++ 图形控制台")
        self.root.geometry("820x620")
        self.root.minsize(720, 520)
        self._configure_badge_styles()

        container = self.ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        header = self.ttk.Frame(container)
        header.pack(fill="x")
        self.ttk.Label(header, text="Codex++ 图形控制台", font=("", 18, "bold")).pack(side="left")
        badge_frame = self.ttk.Frame(header)
        badge_frame.pack(side="right")
        self.cdp_status_label = self.ttk.Label(
            badge_frame,
            textvariable=self.cdp_status_text,
            style="NeutralBadge.TLabel",
        )
        self.cdp_status_label.pack(side="right", padx=(8, 0))
        self.app_status_badge_label = self.ttk.Label(
            badge_frame,
            textvariable=self.app_status_badge_text,
            style="ReadyBadge.TLabel",
        )
        self.app_status_badge_label.pack(side="right")

        main_group = self.ttk.LabelFrame(container, text="常用操作", padding=10)
        main_group.pack(fill="x", pady=(12, 8))
        self._add_button_grid(
            main_group,
            [
                ("安装 Codex++", lambda: self.run_task("setup")),
                ("卸载 Codex++", lambda: self.run_task("remove")),
                ("卸载并删除数据", lambda: self.confirm_and_run_remove_data()),
                ("检查更新", lambda: self.run_task("check_update")),
                ("执行更新", lambda: self.run_task("update")),
                ("更新源码", lambda: self.run_task("source_update")),
            ],
        )

        launch_group = self.ttk.LabelFrame(container, text="启动", padding=10)
        self.launch_group = launch_group
        launch_group.pack(fill="x", pady=8)
        self.launch_button = self._make_button(launch_group, text="启动 Codex++", command=self.start_launch)
        self.launch_button.pack(side="left", padx=(0, 8))
        self.stop_button = self._make_button(
            launch_group,
            text="停止当前启动进程",
            command=self.stop_launch,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=(0, 8))
        self._make_button(launch_group, text="高级设置", command=self.toggle_advanced).pack(side="left")

        self.advanced_frame = self.ttk.LabelFrame(container, text="高级启动设置", padding=10)
        self._build_advanced(self.advanced_frame)

        watcher_group = self.ttk.LabelFrame(container, text="Watcher 自动接管", padding=10)
        watcher_group.pack(fill="x", pady=8)
        if watcher_supported():
            self.ttk.Label(watcher_group, text="Windows watcher 使用现有 CLI 注册/移除系统启动项。").grid(
                row=0,
                column=0,
                columnspan=4,
                sticky="w",
                padx=4,
                pady=(0, 6),
            )
            self._add_button_grid(
                watcher_group,
                [
                    ("安装 watcher", lambda: self.run_task("watch_install")),
                    ("移除 watcher", lambda: self.run_task("watch_remove")),
                    ("启用 watcher", lambda: self.run_task("watch_enable")),
                    ("禁用 watcher", lambda: self.run_task("watch_disable")),
                ],
                start_row=1,
            )
        elif mac_watcher_supported():
            self.ttk.Label(watcher_group, text="macOS watcher 只随当前 GUI 运行，不写入登录项。").grid(
                row=0,
                column=0,
                columnspan=4,
                sticky="w",
                padx=4,
                pady=(0, 6),
            )
            self.mac_watcher_status_label = self.ttk.Label(
                watcher_group,
                textvariable=self.mac_watcher_badge_text,
                style="NeutralBadge.TLabel",
            )
            self.mac_watcher_status_label.grid(
                row=1,
                column=0,
                columnspan=4,
                sticky="w",
                padx=4,
                pady=(0, 6),
            )
            self.mac_watcher_start_button = self._make_button(
                watcher_group,
                text="开启 macOS watcher",
                command=self.start_mac_watcher,
            )
            self.mac_watcher_start_button.grid(row=2, column=0, sticky="ew", padx=4, pady=4)
            self.mac_watcher_stop_button = self._make_button(
                watcher_group,
                text="关闭 macOS watcher",
                command=self.stop_mac_watcher,
                state="disabled",
            )
            self.mac_watcher_stop_button.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
            for column in range(4):
                watcher_group.columnconfigure(column, weight=1)
        else:
            self.ttk.Label(watcher_group, text="watcher 仅支持 Windows，当前平台不可用。").grid(
                row=0,
                column=0,
                columnspan=4,
                sticky="w",
                padx=4,
                pady=(0, 6),
            )
            self._add_button_grid(
                watcher_group,
                [
                    ("安装 watcher", lambda: None),
                    ("移除 watcher", lambda: None),
                    ("启用 watcher", lambda: None),
                    ("禁用 watcher", lambda: None),
                ],
                disabled=True,
                start_row=1,
            )

        log_group = self.ttk.LabelFrame(container, text="日志", padding=8)
        log_group.pack(fill="both", expand=True, pady=(8, 0))
        self.log_text = self.scrolledtext.ScrolledText(log_group, height=14, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self._configure_log_text()

    def _configure_badge_styles(self) -> None:
        style = self.ttk.Style()
        style.configure("ReadyBadge.TLabel", foreground="#16833a")
        style.configure("BusyBadge.TLabel", foreground="#a15c00")
        style.configure("RunningBadge.TLabel", foreground="#0b63ce")
        style.configure("StoppingBadge.TLabel", foreground="#6b5f00")
        style.configure("WarningBadge.TLabel", foreground="#b45309")
        style.configure("NeutralBadge.TLabel", foreground="#6b7280")
        style.configure(
            "Codex.TButton",
            foreground="#1f2328",
            padding=(10, 4),
        )
        style.map(
            "Codex.TButton",
            foreground=[
                ("disabled", "#a8adb5"),
                ("active", "#111827"),
                ("!disabled", "#1f2328"),
            ],
            relief=[
                ("pressed", "sunken"),
                ("disabled", "flat"),
                ("!disabled", "raised"),
            ],
        )

    def _configure_log_text(self) -> None:
        if self.log_text is None:
            return
        self.log_text.configure(
            takefocus=0,
            highlightthickness=0,
            insertwidth=0,
            state="disabled",
        )

    def _make_button(self, parent, text: str, command: Callable[[], None], **kwargs):
        initial_state = kwargs.pop("state", "normal")
        button = None

        def clear_focus() -> None:
            if button is not None:
                button.state(["!focus"])
            self.root.focus_set()

        def wrapped_command() -> None:
            try:
                command()
            finally:
                self.root.after_idle(clear_focus)
                self.root.after(50, clear_focus)

        kwargs.setdefault("takefocus", False)
        kwargs.setdefault("style", "Codex.TButton")
        button = self.ttk.Button(parent, text=text, command=wrapped_command, **kwargs)
        button.bind("<FocusIn>", lambda event: self.root.after_idle(clear_focus), add="+")
        button.bind("<ButtonRelease-1>", lambda event: self.root.after(50, clear_focus), add="+")
        self._set_button_enabled(button, initial_state != "disabled")
        return button

    def _set_button_enabled(self, button, enabled: bool) -> None:
        button.configure(
            state="normal" if enabled else "disabled",
            cursor="pointinghand" if enabled else "arrow",
            style="Codex.TButton",
        )

    def _add_button_grid(
        self,
        parent,
        items: list[tuple[str, Callable[[], None]]],
        disabled: bool = False,
        start_row: int = 0,
    ) -> None:
        for index, (label, command) in enumerate(items):
            button = self._make_button(parent, text=label, command=command)
            if disabled:
                self._set_button_enabled(button, False)
            button.grid(row=start_row + index // 4, column=index % 4, sticky="ew", padx=4, pady=4)
        for column in range(4):
            parent.columnconfigure(column, weight=1)

    def _build_advanced(self, parent) -> None:
        rows = [
            ("Codex App 路径", self.app_dir, "dir"),
            ("Debug 端口", self.debug_port, None),
            ("Helper 端口", self.helper_port, None),
            ("SQLite 数据库", self.db, "file"),
            ("备份目录", self.backup_dir, "dir"),
        ]
        for row, (label, variable, picker) in enumerate(rows):
            self.ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            self.ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
            if picker == "dir":
                command = lambda var=variable: self.choose_directory(var)
                self._make_button(parent, text="选择", command=command).grid(row=row, column=2, padx=(8, 0), pady=4)
            elif picker == "file":
                command = lambda var=variable: self.choose_file(var)
                self._make_button(parent, text="选择", command=command).grid(row=row, column=2, padx=(8, 0), pady=4)
        parent.columnconfigure(1, weight=1)

    def choose_directory(self, variable) -> None:
        path = self.filedialog.askdirectory()
        if path:
            variable.set(path)

    def choose_file(self, variable) -> None:
        path = self.filedialog.askopenfilename()
        if path:
            variable.set(path)

    def toggle_advanced(self) -> None:
        if self.advanced_frame is None:
            return
        if self.advanced_visible.get():
            self.advanced_frame.pack_forget()
            self.advanced_visible.set(False)
        else:
            self.advanced_frame.pack(fill="x", pady=8, after=self.launch_group)
            self.advanced_visible.set(True)

    def launch_options(self) -> LaunchOptions:
        return LaunchOptions(
            app_dir=self.app_dir.get(),
            debug_port=self.debug_port.get(),
            helper_port=self.helper_port.get(),
            db=self.db.get(),
            backup_dir=self.backup_dir.get(),
        )

    def confirm_and_run_remove_data(self) -> None:
        confirmed = self.messagebox.askyesno("确认卸载", "这会删除 Codex++ 自己的日志和备份数据，确定继续吗？")
        if confirmed:
            self.run_task("remove_data")

    def run_task(self, action: str) -> None:
        if self.task_process.is_running():
            self.show_error("已有操作正在执行，请等待完成。")
            return
        command = build_action_command(action)
        self._append_log("$ " + " ".join(command))
        self._set_status("正在执行操作...")
        self.task_process.start(
            command,
            cwd=PROJECT_ROOT,
            output=lambda line: self.output_queue.put(("log", line)),
            finished=lambda code: self.output_queue.put(("task_finished", code)),
        )

    def start_launch(self) -> None:
        if self.launch_process.is_running():
            self.show_error("Codex++ 已在启动中，请先停止当前进程。")
            return
        try:
            command = build_launch_command(self.launch_options())
        except ValueError as exc:
            self.show_error(str(exc))
            return
        self._append_log("$ " + " ".join(command))
        self._set_status("Codex++ 启动中")
        self._set_launch_running(True)
        self.launch_process.start(
            command,
            cwd=PROJECT_ROOT,
            output=lambda line: self.output_queue.put(("log", line)),
            finished=lambda code: self.output_queue.put(("launch_finished", code)),
        )

    def stop_launch(self) -> None:
        if self.launch_process.terminate():
            self._append_log("已请求停止当前启动进程。")
            self._set_status("正在停止 Codex++")
        else:
            self._append_log("当前没有运行中的启动进程。")

    def start_mac_watcher(self) -> None:
        if self.mac_watcher is not None and self.mac_watcher.is_running():
            self.show_error("macOS watcher 已在运行。")
            return
        try:
            options = self.launch_options()
            launch_debug_port(options)
        except ValueError as exc:
            self.show_error(str(exc))
            return
        self.mac_watcher = MacWatcher(
            options,
            self.launch_process,
            output=lambda line: self.output_queue.put(("log", line)),
            status=lambda text: self.output_queue.put(("mac_watcher_status", text)),
            launch_started=lambda: self.output_queue.put(("launch_started", None)),
            launch_finished=lambda code: self.output_queue.put(("launch_finished", code)),
        )
        self.mac_watcher.start()
        self._set_mac_watcher_running(True)

    def stop_mac_watcher(self) -> None:
        if self.mac_watcher is not None and self.mac_watcher.is_running():
            self.mac_watcher.stop()
        self._set_mac_watcher_running(False)

    def close(self) -> None:
        if self.launch_process.is_running():
            confirmed = self.messagebox.askyesno("确认退出", "Codex++ 启动进程仍在运行，退出会停止当前进程。确定退出吗？")
            if not confirmed:
                return
            self.launch_process.terminate()
        if self.mac_watcher is not None and self.mac_watcher.is_running():
            self.mac_watcher.stop()
        self.root.destroy()

    def show_error(self, message: str) -> None:
        self.messagebox.showerror("Codex++", message)

    def _set_status(self, status: str) -> None:
        self.status_text.set(status)
        self.app_status_badge_text.set(format_app_status(status))
        if self.app_status_badge_label is not None:
            self.app_status_badge_label.configure(style=app_status_badge_style(status))

    def _refresh_cdp_status(self) -> None:
        port: int | None = None
        listening: bool | None = None
        try:
            port = launch_debug_port(self.launch_options())
            listening = cdp_listening(port, timeout=CDP_STATUS_TIMEOUT_SECONDS)
        except ValueError:
            port = None
            listening = None
        except Exception:
            listening = None
        self.cdp_status_text.set(format_cdp_status(port, listening))
        if self.cdp_status_label is not None:
            self.cdp_status_label.configure(style=cdp_status_badge_style(listening))
        self.root.after(CDP_STATUS_REFRESH_MS, self._refresh_cdp_status)

    def _set_launch_running(self, running: bool) -> None:
        if self.launch_button is not None:
            self._set_button_enabled(self.launch_button, not running)
        if self.stop_button is not None:
            self._set_button_enabled(self.stop_button, running)

    def _set_mac_watcher_running(self, running: bool) -> None:
        if self.mac_watcher_start_button is not None:
            self._set_button_enabled(self.mac_watcher_start_button, not running)
        if self.mac_watcher_stop_button is not None:
            self._set_button_enabled(self.mac_watcher_stop_button, running)
        self._set_mac_watcher_status("macOS watcher 已开启" if running else "macOS watcher 未开启")

    def _set_mac_watcher_status(self, status: str) -> None:
        self.mac_watcher_status.set(status)
        self.mac_watcher_badge_text.set(format_watcher_status(status))
        if self.mac_watcher_status_label is not None:
            self.mac_watcher_status_label.configure(style=watcher_status_badge_style(status))

    def _append_log(self, line: str) -> None:
        if self.log_text is None:
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _drain_output_queue(self) -> None:
        while True:
            try:
                kind, payload = self.output_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self._append_log(str(payload))
            elif kind == "launch_started":
                self._set_status("Codex++ 启动中")
                self._set_launch_running(True)
            elif kind == "mac_watcher_status":
                self._set_mac_watcher_status(str(payload))
            elif kind == "task_finished":
                self._append_log(f"操作已结束，退出码：{payload}")
                self._set_status("就绪")
            elif kind == "launch_finished":
                self._append_log(f"Codex++ 启动进程已退出，退出码：{payload}")
                self._set_status("就绪")
                self._set_launch_running(False)
        self.root.after(100, self._drain_output_queue)


def main() -> int:
    tk, _, _, messagebox, _ = _import_tkinter()
    try:
        root = tk.Tk()
    except Exception as exc:
        print(f"无法启动图形界面：{exc}", file=sys.stderr)
        return 1
    try:
        CodexPlusGuiApp(root)
        root.mainloop()
        return 0
    except Exception as exc:
        messagebox.showerror("Codex++", f"图形界面运行失败：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
