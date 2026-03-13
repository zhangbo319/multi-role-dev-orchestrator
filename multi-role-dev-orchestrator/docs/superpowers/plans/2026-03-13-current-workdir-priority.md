# Current Workdir Priority Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `multi-role-dev-orchestrator` 在执行时默认以用户当前工作目录作为项目根目录与产物输出根目录，同时保留显式参数覆盖能力。

**Architecture:** 在配置加载阶段引入运行时覆盖逻辑，优先使用显式参数，其次使用执行时当前工作目录，最后才回退到配置文件里的静态值。初始化脚本仍负责生成默认配置，但不再决定后续执行的唯一目录。

**Tech Stack:** Python 3.9、unittest、Codex CLI、Markdown 文档

---

## Chunk 1: 运行时目录优先级

### Task 1: 为当前工作目录优先级补失败测试

**Files:**
- Modify: `multi-role-dev-orchestrator/tests/test_orchestrator_lib.py`
- Modify: `multi-role-dev-orchestrator/scripts/orchestrator_lib.py`
- Modify: `multi-role-dev-orchestrator/scripts/orchestrate.py`

- [ ] **Step 1: 写失败测试**

```python
def test_load_config_prefers_runtime_cwd_over_config_workspace():
    ...

def test_orchestrate_uses_runtime_cwd_for_run_dir():
    ...
```

- [ ] **Step 2: 运行测试，确认因当前实现仍依赖配置文件静态路径而失败**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `FAIL`

- [ ] **Step 3: 实现最小代码**

```python
# 优先级：显式 project_root > runtime_cwd > config workspace_root
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

## Chunk 2: 文档同步

### Task 2: 更新 README 与 skill 说明

**Files:**
- Modify: `README.md`
- Modify: `multi-role-dev-orchestrator/SKILL.md`

- [ ] **Step 1: 写失败测试，约束文档必须声明“默认使用执行时当前工作目录”**

```python
def test_readme_mentions_current_workdir_priority():
    ...
```

- [ ] **Step 2: 运行测试，确认当前文档不满足要求**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `FAIL`

- [ ] **Step 3: 更新文档**

```text
默认以执行命令时的当前工作目录作为项目根目录和产物输出目录
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

## Chunk 3: 端到端验证

### Task 3: 验证产物落点

**Files:**
- No file changes

- [ ] **Step 1: 运行完整测试**

Run: `python3 -m unittest discover -s multi-role-dev-orchestrator/tests -v`
Expected: `OK`

- [ ] **Step 2: 在临时目录验证初始化与 dry-run**

Run:

```bash
tmpdir=$(mktemp -d)
python3 multi-role-dev-orchestrator/scripts/init_project.py --project-root "$tmpdir/project-a"
cd "$tmpdir/project-b"
python3 /path/to/orchestrate.py --config ../project-a/.codex/multi-role-dev/config.json --request "..." --dry-run
```

Expected: 生成目录落在 `project-b/.codex/multi-role-dev/runs/...`
