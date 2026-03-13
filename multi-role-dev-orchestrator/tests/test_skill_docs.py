import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class SkillDocsTest(unittest.TestCase):
    def test_skill_doc_mentions_project_local_config_path(self):
        skill_doc = (ROOT_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("<project>/.codex/multi-role-dev/config.json", skill_doc)
        self.assertIn("python3 ~/.codex/skills/multi-role-dev-orchestrator/scripts/init_project.py", skill_doc)
        self.assertIn("不要与开放式头脑风暴或自由多 agent 讨论混用", skill_doc)

    def test_agent_prompt_mentions_explicit_skill_invocation(self):
        agent_yaml = (ROOT_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("使用 $multi-role-dev-orchestrator", agent_yaml)
        self.assertIn("四角色串行研发流程", agent_yaml)
        self.assertIn("避免切换到其它 skill", agent_yaml)

    def test_config_example_uses_project_relative_placeholder(self):
        config_example = (ROOT_DIR / "references" / "config-example.json").read_text(
            encoding="utf-8"
        )

        self.assertIn("<project>", config_example)
        self.assertIn(".codex/multi-role-dev/runs", config_example)

    def test_docs_mention_current_workdir_priority(self):
        readme = (ROOT_DIR.parent / "README.md").read_text(encoding="utf-8")
        skill_doc = (ROOT_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("默认以执行命令时的当前工作目录作为项目根目录和产物输出目录", readme)
        self.assertIn("默认以执行命令时的当前工作目录作为项目根目录和产物输出目录", skill_doc)


if __name__ == "__main__":
    unittest.main()
