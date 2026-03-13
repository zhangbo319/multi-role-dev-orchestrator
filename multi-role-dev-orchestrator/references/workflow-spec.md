# 工作流规范

## 目录结构

每次运行都会在 `runs_root/<run-id>/` 下生成：

```text
<run-id>/
  run.json
  request.md
  prompts/
    product.prompt.md
    architecture.prompt.md
    development.prompt.md
    testing.prompt.md
    synthesis.prompt.md
  outputs/
    product.md
    architecture.md
    development.md
    testing.md
    synthesis.md
  logs/
    product.log
    architecture.log
    development.log
    testing.log
    synthesis.log
```

## 角色流转顺序

默认 DAG：

```text
product -> architecture -> (development, testing) -> synthesis
```

其中：

- `architecture` 依赖 `product`
- `development` 依赖 `product` 和 `architecture`
- `testing` 依赖 `product` 和 `architecture`
- `synthesis` 依赖 `product`、`architecture`、`development`、`testing`

同一层中的多个角色会并行执行。

## 配置要求

配置文件使用 JSON。

推荐在项目根目录通过初始化脚本生成默认配置，默认路径为：

```text
<project>/.codex/multi-role-dev/config.json
```

最小字段：

- `workspace_root`
- `runs_root`
- `command_template`

可选字段：

- `model`
- `sandbox`
- `roles`
- `role_overrides`

`roles` 支持两种形式：

- legacy 数组：`["product", "architecture", "development", "testing"]`
- DAG 对象：键为角色名，值为 `{ "depends_on": [...] }`

## 命令模板占位符

`command_template` 支持以下占位符：

- `{workspace}`：业务工作区
- `{response_file}`：当前角色输出文件
- `{output_file}`：当前角色输出文件，等价于 `response_file`
- `{log_file}`：当前角色日志文件
- `{role}`：当前角色标识
- `{run_dir}`：当前运行目录

## 失败处理

- 某角色执行失败时立即停止后续阶段
- 已生成产物和日志应保留
- 修改配置或上游产物后可重新执行同一 `run-id`
