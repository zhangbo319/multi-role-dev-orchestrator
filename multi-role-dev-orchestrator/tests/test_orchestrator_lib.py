import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import orchestrator_lib  # type: ignore  # noqa: E402


class OrchestratorLibConfigTest(unittest.TestCase):
    def test_load_config_accepts_generated_project_config(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "demo-project"
            config_dir = project_root / ".codex" / "multi-role-dev"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace_root": str(project_root),
                        "runs_root": str(config_dir / "runs"),
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
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            config = orchestrator_lib.load_config(
                config_path,
                runtime_project_root=project_root,
            )

            self.assertEqual(config["workspace_root"], str(project_root.resolve()))
            self.assertEqual(config["runs_root"], str((config_dir / "runs").resolve()))
            self.assertEqual(config["roles"], orchestrator_lib.ROLE_SEQUENCE)
            self.assertEqual(config["role_overrides"], {})

    def test_load_config_prefers_runtime_cwd_over_config_workspace(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            configured_root = tmp_path / "configured-project"
            runtime_root = tmp_path / "runtime-project"
            config_dir = configured_root / ".codex" / "multi-role-dev"
            config_dir.mkdir(parents=True)
            runtime_root.mkdir()
            config_path = config_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace_root": str(configured_root),
                        "runs_root": str(config_dir / "runs"),
                        "command_template": [
                            "codex",
                            "exec",
                            "--cd",
                            "{workspace}",
                            "-o",
                            "{response_file}",
                            "-",
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            config = orchestrator_lib.load_config(
                config_path,
                runtime_project_root=runtime_root,
            )

            self.assertEqual(config["workspace_root"], str(runtime_root.resolve()))
            self.assertEqual(
                config["runs_root"],
                str((runtime_root / ".codex" / "multi-role-dev" / "runs").resolve()),
            )

    def test_orchestrate_uses_runtime_cwd_for_run_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            configured_root = tmp_path / "configured-project"
            runtime_root = tmp_path / "runtime-project"
            config_dir = configured_root / ".codex" / "multi-role-dev"
            config_dir.mkdir(parents=True)
            runtime_root.mkdir()
            config_path = config_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace_root": str(configured_root),
                        "runs_root": str(config_dir / "runs"),
                        "command_template": [
                            "codex",
                            "exec",
                            "--cd",
                            "{workspace}",
                            "-o",
                            "{response_file}",
                            "-",
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            old_cwd = Path.cwd()
            os.chdir(runtime_root)
            try:
                result = orchestrator_lib.orchestrate(
                    request_text="请输出多角色方案",
                    config_path=config_path,
                    run_id="cwd-priority",
                    dry_run=True,
                )
            finally:
                os.chdir(old_cwd)

            self.assertEqual(
                result["run_dir"],
                str(
                    (
                        runtime_root
                        / ".codex"
                        / "multi-role-dev"
                        / "runs"
                        / "cwd-priority"
                    ).resolve()
                ),
            )
            self.assertTrue(
                (
                    runtime_root
                    / ".codex"
                    / "multi-role-dev"
                    / "runs"
                    / "cwd-priority"
                    / "run.json"
                ).exists()
            )

    def test_orchestrate_prefers_explicit_project_root_over_runtime_cwd(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            configured_root = tmp_path / "configured-project"
            runtime_root = tmp_path / "runtime-project"
            explicit_root = tmp_path / "explicit-project"
            config_dir = configured_root / ".codex" / "multi-role-dev"
            config_dir.mkdir(parents=True)
            runtime_root.mkdir()
            explicit_root.mkdir()
            config_path = config_dir / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace_root": str(configured_root),
                        "runs_root": str(config_dir / "runs"),
                        "command_template": [
                            "codex",
                            "exec",
                            "--cd",
                            "{workspace}",
                            "-o",
                            "{response_file}",
                            "-",
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            old_cwd = Path.cwd()
            os.chdir(runtime_root)
            try:
                result = orchestrator_lib.orchestrate(
                    request_text="请输出多角色方案",
                    config_path=config_path,
                    run_id="explicit-priority",
                    dry_run=True,
                    project_root=explicit_root,
                )
            finally:
                os.chdir(old_cwd)

            self.assertEqual(
                result["workspace_root"],
                str(explicit_root.resolve()),
            )
            self.assertEqual(
                result["run_dir"],
                str(
                    (
                        explicit_root
                        / ".codex"
                        / "multi-role-dev"
                        / "runs"
                        / "explicit-priority"
                    ).resolve()
                ),
            )


if __name__ == "__main__":
    unittest.main()
