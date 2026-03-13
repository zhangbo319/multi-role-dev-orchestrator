---
name: multi-role-dev-orchestrator
description: 适用于需要将单个需求固定拆分为产品、架构、开发、测试四角色串行交接的场景。用于生成结构化需求、技术方案、开发计划和测试结论，不用于开放式头脑风暴、自由多 agent 讨论或并行会议式协作。
---

# 多角色研发编排器

## 概览

使用这个 skill 时，优先把问题建模为一个固定四角色串行交接的流程，而不是自由聊天式多 agent 讨论。第一版的目标是让每个角色都产生明确文档产物，便于复查、追踪和继续开发。

推荐显式触发短语：

```text
使用 $multi-role-dev-orchestrator 为当前需求建立四角色串行研发流程
```

如果你已经决定使用本 skill，就不要与开放式头脑风暴或自由多 agent 讨论混用，以免模型切到其它 skill 或回到普通对话模式。

## 工作流

### 第 1 步：确认边界

先确认这次任务是否适合固定四角色：

- `产品`：负责业务目标、用户故事、范围与验收标准
- `架构`：负责模块边界、关键流程、数据流与技术风险
- `开发`：负责实现拆解、目录规划、编码执行与测试建议
- `测试`：负责验收清单、风险场景、回归建议与结论

如果任务需要的是开放式头脑风暴、组织策略讨论或并发会议式协作，不要直接套用本 skill。已经进入本 skill 后，不要与开放式头脑风暴或自由多 agent 讨论混用。

### 第 2 步：准备配置

读取 [workflow-spec.md](./references/workflow-spec.md) 了解运行目录和交接规范，再参考 [config-example.json](./references/config-example.json) 了解配置结构。

必须具备：

- 本机安装可用的 `codex` CLI
- 一份 JSON 配置文件
- 一个可写的工作目录

推荐先在目标项目根目录执行初始化脚本：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/init_project.py \
  --project-root .
```

默认会生成：

```text
<project>/.codex/multi-role-dev/config.json
```

其中：

- `workspace_root` 指向当前项目目录
- `runs_root` 指向 `<project>/.codex/multi-role-dev/runs`
- `command_template` 内置 `codex exec` 的默认模板

如果你已经有项目级配置，可直接复用，不必重复初始化。

初始化脚本只负责生成默认配置。真正执行编排时，默认以执行命令时的当前工作目录作为项目根目录和产物输出目录；如果你在别的目录执行 `orchestrate.py`，产物会落到那个目录下的 `.codex/multi-role-dev/runs/`。

如果需要显式覆盖当前工作目录，可额外传入：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/orchestrate.py \
  --config ./.codex/multi-role-dev/config.json \
  --project-root /path/to/project \
  --request "请为一个直播平台设计多角色协同开发方案" \
  --dry-run
```

### 第 3 步：执行编排

推荐先跑一次 `dry-run`：

```bash
python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/orchestrate.py \
  --config ./.codex/multi-role-dev/config.json \
  --request "请为一个直播平台设计多角色协同开发方案" \
  --run-id demo-run \
  --dry-run
```

这一步会生成：

- 运行目录
- 每个角色的提示词
- 产物目标路径
- 运行清单

确认提示词结构符合预期后，再去掉 `--dry-run` 执行真实编排。

### 第 4 步：检查产物

逐个检查：

- `outputs/product.md`
- `outputs/architecture.md`
- `outputs/development.md`
- `outputs/testing.md`

如果某个角色结果不满足预期，优先修改：

- 角色附加规则
- 配置中的命令模板
- 模板文档或上游产物

## 资源

### `scripts/`

- `orchestrate.py`：创建运行目录并串行执行四角色
- `run_role.py`：单独生成某个角色的提示词
- `orchestrator_lib.py`：配置解析、提示词构建、命令渲染与执行逻辑
- `init_project.py`：为任意项目生成 `<project>/.codex/multi-role-dev/config.json`

### `references/`

- [role-definitions.md](./references/role-definitions.md)：四角色职责与交接要求
- [workflow-spec.md](./references/workflow-spec.md)：目录结构、配置与运行规则
- [config-example.json](./references/config-example.json)：项目级配置结构示例

### `assets/`

- `prd.template.md`
- `architecture.template.md`
- `development-plan.template.md`
- `test-report.template.md`

使用这些模板约束角色输出结构，减少上游产物质量波动。
