import json
import subprocess
from datetime import datetime
from pathlib import Path


ROLE_SEQUENCE = ["product", "architecture", "development", "testing"]

ROLE_LABELS = {
    "product": "产品",
    "architecture": "架构",
    "development": "开发",
    "testing": "测试",
}

ROLE_DEPENDENCIES = {
    "product": [],
    "architecture": ["product"],
    "development": ["product", "architecture"],
    "testing": ["product", "architecture", "development"],
}

ROLE_EXPECTATIONS = {
    "product": [
        "输出目标与背景",
        "输出用户故事与范围边界",
        "输出验收标准",
    ],
    "architecture": [
        "输出模块划分与职责边界",
        "输出关键数据流与技术取舍",
        "识别架构风险",
    ],
    "development": [
        "输出实现拆解与建议目录",
        "输出开发顺序与测试建议",
        "标注风险和待确认事项",
    ],
    "testing": [
        "输出验收检查清单",
        "输出关键测试场景",
        "输出结论与回归建议",
    ],
}


def default_runs_root(project_root):
    return Path(project_root).resolve() / ".codex" / "multi-role-dev" / "runs"


def resolve_project_root(runtime_project_root=None):
    if runtime_project_root is None:
        return Path.cwd().resolve()
    return Path(runtime_project_root).resolve()


def load_config(config_path, runtime_project_root=None):
    config_file = Path(config_path)
    data = json.loads(config_file.read_text(encoding="utf-8"))
    required_keys = ["workspace_root", "runs_root", "command_template"]
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ValueError("配置缺少字段: {}".format(", ".join(missing)))

    project_root = resolve_project_root(runtime_project_root)

    config = {
        "workspace_root": str(project_root),
        "runs_root": str(default_runs_root(project_root)),
        "command_template": data["command_template"],
        "model": data.get("model", ""),
        "sandbox": data.get("sandbox", "workspace-write"),
        "roles": data.get("roles", ROLE_SEQUENCE),
        "role_overrides": data.get("role_overrides", {}),
    }
    return config


def render_command(template, variables):
    return [part.format(**variables) for part in template]


def build_role_prompt(role, request_text, artifact_paths, output_path, role_overrides=None):
    role_overrides = role_overrides or {}
    label = ROLE_LABELS[role]
    dependencies = ROLE_DEPENDENCIES[role]
    expectations = ROLE_EXPECTATIONS[role]
    extra_rules = role_overrides.get(role, {}).get("extra_rules", [])

    lines = [
        "# 多角色协同开发任务",
        "",
        "你当前扮演的角色是：{}".format(label),
        "",
        "## 原始需求",
        request_text,
        "",
        "## 上游输入",
    ]

    if dependencies:
        for dependency in dependencies:
            lines.append("- {}：{}".format(ROLE_LABELS[dependency], artifact_paths[dependency]))
    else:
        lines.append("- 无，上游输入仅为原始需求")

    lines.extend(
        [
            "",
            "## 输出要求",
        ]
    )
    for item in expectations:
        lines.append("- {}".format(item))

    if extra_rules:
        lines.extend(["", "## 额外规则"])
        for item in extra_rules:
            lines.append("- {}".format(item))

    lines.extend(
        [
            "",
            "## 输出文件",
            output_path,
            "",
            "请直接围绕上述要求输出完整结果，并确保内容适合下游角色继续使用。",
        ]
    )

    return "\n".join(lines) + "\n"


def default_run_id():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def execute_role_command(role, prompt_text, output_path, log_path, run_dir, config):
    command = render_command(
        config["command_template"],
        {
            "workspace": config["workspace_root"],
            "response_file": output_path,
            "output_file": output_path,
            "log_file": log_path,
            "role": role,
            "run_dir": str(run_dir),
        },
    )
    completed = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        capture_output=True,
        check=False,
    )

    log_content = []
    log_content.append("COMMAND: {}\n".format(" ".join(command)))
    if completed.stdout:
        log_content.append("STDOUT:\n{}\n".format(completed.stdout))
    if completed.stderr:
        log_content.append("STDERR:\n{}\n".format(completed.stderr))
    Path(log_path).write_text("".join(log_content), encoding="utf-8")

    if completed.returncode != 0:
        raise RuntimeError("角色 {} 执行失败，退出码 {}".format(role, completed.returncode))

    output_file = Path(output_path)
    if not output_file.exists():
        output_file.write_text(completed.stdout, encoding="utf-8")


def orchestrate(
    request_text,
    config_path,
    run_id=None,
    dry_run=False,
    execute_role_fn=None,
    project_root=None,
):
    config = load_config(config_path, runtime_project_root=project_root)
    run_id = run_id or default_run_id()
    run_dir = Path(config["runs_root"]) / run_id
    prompts_dir = run_dir / "prompts"
    outputs_dir = run_dir / "outputs"
    logs_dir = run_dir / "logs"

    prompts_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "request.md").write_text(request_text + "\n", encoding="utf-8")

    artifact_paths = {
        role: str(outputs_dir / "{}.md".format(role)) for role in config["roles"]
    }
    manifest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "workspace_root": config["workspace_root"],
        "status": "initialized",
        "roles": config["roles"],
        "artifacts": artifact_paths,
    }

    role_runner = execute_role_fn or execute_role_command
    for role in config["roles"]:
        prompt_text = build_role_prompt(
            role=role,
            request_text=request_text,
            artifact_paths=artifact_paths,
            output_path=artifact_paths[role],
            role_overrides=config["role_overrides"],
        )
        prompt_path = prompts_dir / "{}.prompt.md".format(role)
        prompt_path.write_text(prompt_text, encoding="utf-8")

        if dry_run:
            continue

        role_runner(
            role=role,
            prompt_text=prompt_text,
            output_path=artifact_paths[role],
            log_path=str(logs_dir / "{}.log".format(role)),
            run_dir=run_dir,
            config=config,
        )

    manifest["status"] = "dry-run" if dry_run else "completed"
    write_json(run_dir / "run.json", manifest)
    return manifest
