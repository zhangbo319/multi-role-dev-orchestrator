# multi-role-dev-orchestrator

一个面向 Codex 的多角色研发编排 skill 仓库。仓库内的实际 skill 位于 `multi-role-dev-orchestrator/` 目录，可通过私有 GitHub 仓库安装到 `~/.codex/skills/`。

## 安装

前提：

- 本机已安装 `codex`
- 机器对私有 GitHub 仓库有读取权限
- 已配置可用的 `git` 凭证，或可通过 `GITHUB_TOKEN` / `GH_TOKEN` 访问

### 方式一：直接让 Codex 一键执行安装脚本

如果你已经把这个仓库拉到本地，推荐直接让 Codex 在仓库根目录执行：

```bash
bash scripts/install-codex-skill.sh
```

你也可以直接在 Codex 对话里下达这条指令：

```text
请在当前仓库根目录执行 `bash scripts/install-codex-skill.sh`，把 multi-role-dev-orchestrator 安装到 ~/.codex/skills
```

这个脚本会自动调用 Codex 自带的 `skill-installer`：

- 未安装时执行真实安装
- 已安装时直接返回成功，避免重复报错

脚本位置：

[`scripts/install-codex-skill.sh`](/Users/zhangbo/work/INKE/codex/multi-role-dev-orchestrator/scripts/install-codex-skill.sh)

### 方式二：直接执行单条安装命令

如果你不想依赖仓库脚本，也可以直接执行下面这一条命令：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhangbo319/multi-role-dev-orchestrator \
  --path multi-role-dev-orchestrator \
  --method auto
```

安装完成后，重启 Codex 以加载新 skill。

## 卸载 / 升级 / 重新安装

### 卸载

删除已安装的 skill 目录：

```bash
rm -rf ~/.codex/skills/multi-role-dev-orchestrator
```

你也可以直接在 Codex 对话里下达这条指令：

```text
请删除 ~/.codex/skills/multi-role-dev-orchestrator，并提醒我重启 Codex
```

删除完成后，重启 Codex 以移除这个 skill。

### 重新安装

当本地安装损坏、需要强制覆盖，或想重新走一次完整安装链路时，推荐先卸载再安装：

```bash
rm -rf ~/.codex/skills/multi-role-dev-orchestrator
bash scripts/install-codex-skill.sh
```

你也可以直接在 Codex 对话里下达这条指令：

```text
请先删除 ~/.codex/skills/multi-role-dev-orchestrator，再执行 `bash scripts/install-codex-skill.sh` 重新安装这个 skill
```

重新安装完成后，重启 Codex 以加载最新版本。

### 升级

当前推荐把“升级”视为“安装仓库最新版本”：

1. 先拉取这个仓库的最新代码
2. 删除本地已安装的旧版本 skill
3. 重新执行安装脚本

示例命令：

```bash
git pull
rm -rf ~/.codex/skills/multi-role-dev-orchestrator
bash scripts/install-codex-skill.sh
```

你也可以直接在 Codex 对话里下达这条指令：

```text
请先拉取当前仓库最新代码，再删除 ~/.codex/skills/multi-role-dev-orchestrator，并执行 `bash scripts/install-codex-skill.sh` 完成升级
```

升级完成后，重启 Codex 以加载最新版本。

## 使用

在任意项目根目录初始化配置：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/init_project.py \
  --project-root .
```

默认会生成：

```text
<project>/.codex/multi-role-dev/config.json
```

初始化脚本只负责生成默认配置。真正执行编排时，默认以执行命令时的当前工作目录作为项目根目录和产物输出目录；如果你在别的目录执行 `orchestrate.py`，产物会落到那个目录下的 `.codex/multi-role-dev/runs/`。

如果你需要显式覆盖当前工作目录，可以传入：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/orchestrate.py \
  --config /path/to/config.json \
  --project-root /path/to/project \
  --request "请为一个直播平台设计多角色协同开发方案" \
  --dry-run
```

建议先跑一次 `dry-run`：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/orchestrate.py \
  --config ./.codex/multi-role-dev/config.json \
  --request "请为一个直播平台设计多角色协同开发方案" \
  --run-id demo-run \
  --dry-run
```

推荐显式触发短语：

```text
使用 $multi-role-dev-orchestrator 为当前需求建立四角色串行研发流程
```

为了避免和其它 skill 冲突，进入本 skill 后不要混用开放式头脑风暴或自由多 agent 讨论。
