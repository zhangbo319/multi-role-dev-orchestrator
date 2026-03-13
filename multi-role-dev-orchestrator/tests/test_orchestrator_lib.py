import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import orchestrator_lib  # type: ignore  # noqa: E402


class OrchestratorLibConfigTest(unittest.TestCase):
    def test_load_config_uses_default_dag_roles(self):
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
                        "command_template": ["codex", "exec", "-"],
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

            self.assertIn("synthesis", config["roles"])
            self.assertEqual(config["roles"]["testing"]["depends_on"], ["product", "architecture"])
            self.assertEqual(
                config["roles"]["synthesis"]["depends_on"],
                ["product", "architecture", "development", "testing"],
            )

    def test_legacy_role_list_maps_to_serial_dependencies(self):
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
                        "command_template": ["codex", "exec", "-"],
                        "roles": ["product", "architecture", "development", "testing"],
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

            self.assertEqual(config["roles"]["architecture"]["depends_on"], ["product"])
            self.assertEqual(config["roles"]["development"]["depends_on"], ["product", "architecture"])
            self.assertEqual(
                config["roles"]["testing"]["depends_on"],
                ["product", "architecture", "development"],
            )

    def test_build_execution_stages_for_default_dag(self):
        stages = orchestrator_lib.build_execution_stages(orchestrator_lib.DEFAULT_ROLE_GRAPH)
        self.assertEqual(
            stages,
            [
                ["product"],
                ["architecture"],
                ["development", "testing"],
                ["synthesis"],
            ],
        )

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
            self.assertEqual(
                list(config["roles"].keys()),
                list(orchestrator_lib.DEFAULT_ROLE_GRAPH.keys()),
            )
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

    def test_orchestrate_default_dag_includes_synthesis_artifact(self):
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
                        "command_template": ["codex", "exec", "-"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = orchestrator_lib.orchestrate(
                request_text="请输出多角色方案",
                config_path=config_path,
                run_id="dag-default",
                dry_run=True,
                project_root=project_root,
            )

            self.assertIn("synthesis", result["artifacts"])
            self.assertTrue(
                (
                    project_root
                    / ".codex"
                    / "multi-role-dev"
                    / "runs"
                    / "dag-default"
                    / "prompts"
                    / "synthesis.prompt.md"
                ).exists()
            )

    def test_orchestrate_runs_parallel_roles_in_same_stage(self):
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
                        "command_template": ["codex", "exec", "-"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            barrier = threading.Barrier(2, timeout=0.5)
            call_order = []
            lock = threading.Lock()

            def fake_execute_role(role, prompt_text, output_path, log_path, run_dir, config):
                with lock:
                    call_order.append(role)
                Path(output_path).write_text(role + "\n", encoding="utf-8")
                Path(log_path).write_text(role + "\n", encoding="utf-8")
                if role in {"development", "testing"}:
                    barrier.wait()
                    time.sleep(0.05)

            result = orchestrator_lib.orchestrate(
                request_text="请输出多角色方案",
                config_path=config_path,
                run_id="parallel-stage",
                dry_run=False,
                execute_role_fn=fake_execute_role,
                project_root=project_root,
            )

            self.assertEqual(call_order[0:2], ["product", "architecture"])
            self.assertCountEqual(call_order[2:4], ["development", "testing"])
            self.assertEqual(call_order[4], "synthesis")
            self.assertIn("synthesis", result["artifacts"])

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
