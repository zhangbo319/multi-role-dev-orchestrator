import argparse
import json
from pathlib import Path


DEFAULT_CONFIG_DIR = Path(".codex") / "multi-role-dev"


def build_default_config(project_root):
    project_root = Path(project_root).resolve()
    runs_root = project_root / DEFAULT_CONFIG_DIR / "runs"
    return {
        "workspace_root": str(project_root),
        "runs_root": str(runs_root),
        "command_template": [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write",
            "--cd",
            "{workspace}",
            "-o",
            "{response_file}",
            "-",
        ],
        "model": "",
        "sandbox": "workspace-write",
        "role_overrides": {
            "product": {
                "extra_rules": [
                    "必须明确哪些需求属于第一版，哪些属于后续迭代"
                ]
            },
            "architecture": {
                "extra_rules": [
                    "必须给出模块边界和关键接口"
                ]
            },
            "development": {
                "extra_rules": [
                    "必须给出建议文件路径和开发顺序"
                ]
            },
            "testing": {
                "extra_rules": [
                    "必须覆盖异常场景和回归策略"
                ]
            },
        },
    }


def initialize_project(project_root, force=False):
    project_root = Path(project_root).resolve()
    config_dir = project_root / DEFAULT_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"

    if config_path.exists() and not force:
        return config_path

    payload = build_default_config(project_root)
    config_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return config_path


def parse_args():
    parser = argparse.ArgumentParser(description="为当前项目初始化多角色研发编排配置")
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录，默认当前目录",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="如果配置已存在则覆盖",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config_path = initialize_project(args.project_root, force=args.force)
    print(str(config_path))


if __name__ == "__main__":
    main()
