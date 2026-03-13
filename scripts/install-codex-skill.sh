#!/usr/bin/env bash

set -euo pipefail

SKILL_NAME="multi-role-dev-orchestrator"
REPO="zhangbo319/multi-role-dev-orchestrator"
SKILL_PATH="multi-role-dev-orchestrator"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
INSTALLER="$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py"
DEST_DIR="$CODEX_HOME/skills/$SKILL_NAME"

if [[ ! -f "$INSTALLER" ]]; then
  echo "未找到 Codex skill 安装器: $INSTALLER" >&2
  echo "请先确认本机已安装 Codex，且 ~/.codex/skills/.system/skill-installer 可用。" >&2
  exit 1
fi

if [[ -d "$DEST_DIR" ]]; then
  echo "Skill 已安装: $DEST_DIR"
  echo "如果需要重新安装，请先删除该目录后再重试。"
  exit 0
fi

python3 "$INSTALLER" \
  --repo "$REPO" \
  --path "$SKILL_PATH" \
  --method auto

echo "安装完成后，请重启 Codex 以加载新 skill。"
