import argparse
import json
from pathlib import Path

import orchestrator_lib


def parse_args():
    parser = argparse.ArgumentParser(description="多角色研发编排器")
    parser.add_argument("--config", required=True, help="JSON 配置文件路径")
    parser.add_argument("--request-file", help="需求文件路径")
    parser.add_argument("--request", help="直接传入需求文本")
    parser.add_argument("--run-id", help="指定运行 ID")
    parser.add_argument(
        "--project-root",
        help="显式指定项目根目录；默认使用执行命令时的当前工作目录",
    )
    parser.add_argument("--dry-run", action="store_true", help="只生成提示词与目录")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.request and not args.request_file:
        raise SystemExit("请提供 --request 或 --request-file")

    request_text = args.request
    if args.request_file:
        request_text = Path(args.request_file).read_text(encoding="utf-8")

    result = orchestrator_lib.orchestrate(
        request_text=request_text,
        config_path=args.config,
        run_id=args.run_id,
        dry_run=args.dry_run,
        project_root=args.project_root,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
