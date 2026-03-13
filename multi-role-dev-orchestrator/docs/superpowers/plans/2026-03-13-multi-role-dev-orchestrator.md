# Multi-Role Dev Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `multi-role-dev-orchestrator` 支持通过私有 GitHub 仓库安装，并能在任意项目目录一键初始化配置后直接运行，同时通过更明确的提示词降低与其它 skill 的冲突。

**Architecture:** 保持四角色串行编排模型不变，只补齐可移植性、初始化入口、使用约束和验证测试。Python 脚本负责项目初始化与路径解析，`SKILL.md` 和 `agents/openai.yaml` 负责触发与使用说明。

**Tech Stack:** Python 3.9、unittest、Codex skill 目录结构、git、GitHub 私有仓库

---

## Chunk 1: 基线与测试护栏

### Task 1: 为初始化和配置行为补测试

**Files:**
- Create: `tests/test_orchestrator_lib.py`
- Create: `tests/test_init_project.py`
- Modify: `scripts/orchestrator_lib.py`
- Create: `scripts/init_project.py`

- [ ] **Step 1: 写失败测试，覆盖项目配置生成与配置加载**

```python
def test_init_project_writes_config_under_project_codex_dir():
    ...

def test_load_config_accepts_generated_project_config():
    ...
```

- [ ] **Step 2: 运行测试，确认因功能缺失或行为不匹配而失败**

Run: `python3 -m unittest discover -s tests -v`
Expected: `FAIL` 或 `ERROR`，指出缺少初始化脚本或配置结构不满足预期

- [ ] **Step 3: 实现最小初始化与配置支持**

```python
# 生成 <project>/.codex/multi-role-dev/config.json
# 根据当前项目目录构建 workspace_root / runs_root / command_template
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s tests -v`
Expected: `OK`

## Chunk 2: 可移植运行与提示词触发

### Task 2: 调整 skill 文档与 UI 元数据

**Files:**
- Modify: `SKILL.md`
- Modify: `agents/openai.yaml`
- Modify: `references/config-example.json`

- [ ] **Step 1: 写失败测试，约束文档中必须出现新的初始化路径和触发短语**

```python
def test_skill_doc_mentions_project_local_config_path():
    ...

def test_agent_prompt_mentions_explicit_skill_invocation():
    ...
```

- [ ] **Step 2: 运行测试，确认当前文案不满足要求**

Run: `python3 -m unittest discover -s tests -v`
Expected: `FAIL`

- [ ] **Step 3: 修改文档与元数据，补齐安装后使用方式和防冲突提示**

```text
使用 $multi-role-dev-orchestrator 为当前需求建立四角色串行研发流程
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover -s tests -v`
Expected: `OK`

## Chunk 3: 端到端验证与仓库交付

### Task 3: 验证脚本、初始化仓库并推送远端

**Files:**
- Modify: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: 运行完整验证**

Run: `python3 -m unittest discover -s tests -v`
Expected: `OK`

Run: `python3 scripts/orchestrate.py --help`
Expected: exit `0`

Run: `python3 scripts/init_project.py --help`
Expected: exit `0`

- [ ] **Step 2: 初始化 git 仓库并提交首个可用版本**

```bash
git init
git add .
git commit -m "feat: prepare multi-role dev orchestrator for portable installation"
```

- [ ] **Step 3: 绑定远端并推送**

```bash
git branch -M main
git remote add origin https://github.com/zhangbo319/multi-role-dev-orchestrator.git
git push -u origin main
```
