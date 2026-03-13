import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import init_project  # type: ignore  # noqa: E402


class InitProjectTest(unittest.TestCase):
    def test_init_project_writes_config_under_project_codex_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "demo-project"
            project_root.mkdir()

            config_path = init_project.initialize_project(project_root)

            expected_path = (project_root / ".codex" / "multi-role-dev" / "config.json").resolve()
            self.assertEqual(config_path, expected_path)
            self.assertTrue(config_path.exists())

            payload = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["workspace_root"], str(project_root.resolve()))
            self.assertEqual(
                payload["runs_root"],
                str((project_root / ".codex" / "multi-role-dev" / "runs").resolve()),
            )
            self.assertEqual(payload["sandbox"], "workspace-write")
            self.assertIn("{workspace}", payload["command_template"])
            self.assertIn("{response_file}", payload["command_template"])


if __name__ == "__main__":
    unittest.main()
