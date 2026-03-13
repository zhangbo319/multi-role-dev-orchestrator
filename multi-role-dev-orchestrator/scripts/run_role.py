import argparse
import json
from pathlib import Path

import orchestrator_lib


def parse_args():
    parser = argparse.ArgumentParser(description="单角色提示词生成器")
    parser.add_argument("--role", required=True, choices=orchestrator_lib.ROLE_SEQUENCE)
    parser.add_argument("--request-file", required=True, help="需求文件路径")
    parser.add_argument("--output-file", required=True, help="输出文件路径")
    parser.add_argument(
        "--artifacts-json",
        required=True,
        help="上游产物 JSON，键为角色名，值为文件路径",
    )
    parser.add_argument(
        "--role-overrides-json",
        default="{}",
        help="角色附加规则 JSON",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    request_text = Path(args.request_file).read_text(encoding="utf-8")
    artifact_paths = json.loads(args.artifacts_json)
    role_overrides = json.loads(args.role_overrides_json)
    prompt = orchestrator_lib.build_role_prompt(
        role=args.role,
        request_text=request_text,
        artifact_paths=artifact_paths,
        output_path=args.output_file,
        role_overrides=role_overrides,
    )
    print(prompt)


if __name__ == "__main__":
    main()
