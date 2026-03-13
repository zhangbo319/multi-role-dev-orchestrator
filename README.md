# multi-role-dev-orchestrator

一个面向 Codex 的多角色研发编排 skill 仓库。仓库内的实际 skill 位于 `multi-role-dev-orchestrator/` 目录，可通过私有 GitHub 仓库安装到 `~/.codex/skills/`。

## 安装

前提：

- 本机已安装 `codex`
- 机器对私有 GitHub 仓库有读取权限
- 已配置可用的 `git` 凭证，或可通过 `GITHUB_TOKEN` / `GH_TOKEN` 访问

安装命令：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhangbo319/multi-role-dev-orchestrator \
  --path multi-role-dev-orchestrator \
  --method auto
```

安装完成后，重启 Codex 以加载新 skill。

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
