#!/bin/sh
set -eu

SCRIPT_PATH=$(python3 - "$0" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).expanduser().resolve())
PY
)
PROJECT_ROOT=$(dirname "$SCRIPT_PATH")
cd "$PROJECT_ROOT"

if [ ! -f "$PROJECT_ROOT/codex_plus_gui.py" ]; then
  echo "错误：未在脚本真实路径旁找到 codex_plus_gui.py。"
  echo "请不要把 start_gui.command 复制到桌面；请创建指向项目目录中 start_gui.command 的快捷方式或符号链接。"
  exit 1
fi

VENV_DIR="$PROJECT_ROOT/.venv"
VENV_PY="$VENV_DIR/bin/python"

if [ ! -x "$VENV_PY" ]; then
  echo "Creating Python virtual environment at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

echo "Installing Codex++ into venv..."
"$VENV_PY" -m pip install -e .

echo "Starting Codex++ graphical console..."
"$VENV_PY" "$PROJECT_ROOT/codex_plus_gui.py"
