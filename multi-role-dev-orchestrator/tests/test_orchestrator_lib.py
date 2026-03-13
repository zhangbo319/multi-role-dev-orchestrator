import json
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

            config = orchestrator_lib.load_config(config_path)

            self.assertEqual(config["workspace_root"], str(project_root))
            self.assertEqual(config["runs_root"], str(config_dir / "runs"))
            self.assertEqual(config["roles"], orchestrator_lib.ROLE_SEQUENCE)
            self.assertEqual(config["role_overrides"], {})


if __name__ == "__main__":
    unittest.main()
