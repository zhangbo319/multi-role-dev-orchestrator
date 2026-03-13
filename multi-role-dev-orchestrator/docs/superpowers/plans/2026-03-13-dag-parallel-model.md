# DAG Parallel Model Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `multi-role-dev-orchestrator` 从固定串行四角色升级为依赖图驱动的多 Agent 并行编排模型，并保持旧配置可兼容运行。

**Architecture:** 在配置层引入角色定义与依赖图，在编排层增加 DAG 校验、分层执行和同层并行调度。默认模型升级为 `product -> architecture -> (development, testing) -> synthesis`，旧的角色列表配置继续映射为串行依赖。

**Tech Stack:** Python 3.9、unittest、concurrent.futures、Markdown 文档

---

## Chunk 1: 角色图与兼容层

### Task 1: 为角色图归一化与分层调度补失败测试

**Files:**
- Modify: `multi-role-dev-orchestrator/tests/test_orchestrator_lib.py`
- Modify: `multi-role-dev-orchestrator/scripts/orchestrator_lib.py`

- [ ] **Step 1: 写失败测试**

```python
def test_load_config_uses_default_dag_roles():
    ...

def test_legacy_role_list_maps_to_serial_dependencies():
    ...

def test_build_execution_stages_for_default_dag():
    ...
```

- [ ] **Step 2: 运行测试，确认当前实现仍只有串行角色列表**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `FAIL`

- [ ] **Step 3: 实现最小角色图兼容层**

```python
# 统一把 roles 转成 {role: {depends_on: [...]}} 结构
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

## Chunk 2: 并行执行

### Task 2: 为同层并行执行补失败测试并实现

**Files:**
- Modify: `multi-role-dev-orchestrator/tests/test_orchestrator_lib.py`
- Modify: `multi-role-dev-orchestrator/scripts/orchestrator_lib.py`

- [ ] **Step 1: 写失败测试**

```python
def test_orchestrate_default_dag_includes_synthesis_artifact():
    ...

def test_orchestrate_runs_parallel_roles_in_same_stage():
    ...
```

- [ ] **Step 2: 运行测试，确认当前编排仍按单线程串行执行**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `FAIL`

- [ ] **Step 3: 实现同层并行**

```python
# 使用 ThreadPoolExecutor 并发执行同一层的多个 role
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

## Chunk 3: 文档与默认配置

### Task 3: 更新默认模型说明

**Files:**
- Modify: `README.md`
- Modify: `multi-role-dev-orchestrator/SKILL.md`
- Modify: `multi-role-dev-orchestrator/references/workflow-spec.md`
- Modify: `multi-role-dev-orchestrator/references/role-definitions.md`
- Modify: `multi-role-dev-orchestrator/references/config-example.json`
- Modify: `multi-role-dev-orchestrator/tests/test_skill_docs.py`

- [ ] **Step 1: 写失败测试，约束默认模型和 synthesis 文档说明**

```python
def test_docs_mention_dag_parallel_model():
    ...
```

- [ ] **Step 2: 运行测试，确认当前文档仍描述为固定串行四角色**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `FAIL`

- [ ] **Step 3: 更新文档和示例配置**

```text
product -> architecture -> (development, testing) -> synthesis
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

## Chunk 4: 端到端验证

### Task 4: 验证 DAG 默认模型和兼容模式

**Files:**
- No file changes

- [ ] **Step 1: 运行完整测试**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

- [ ] **Step 2: 验证默认配置会生成 synthesis 产物**

Run: 使用 `dry-run` 检查 `outputs/synthesis.md`

- [ ] **Step 3: 验证 legacy roles 列表配置仍可运行**

Run: 使用 legacy `roles` 数组配置执行 `dry-run`
Expected: 仍为串行依赖，产物完整
