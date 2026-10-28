"""透過新的客戶端，在既有 SpaceClaim gRPC 工作階段執行指定原生腳本。"""

import argparse
import json
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--args-json", default="{}", help="鍵和值都必須是字串的 JSON 物件")
    parser.add_argument("--connect-timeout", type=int, default=60)
    parser.add_argument("--max-message-mib", type=int, help="選用，建立客戶端前設定接收上限")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("port 必須介於 1 與 65535")
    if not args.script.is_file():
        parser.error("script 必須是存在的原生腳本檔案")
    if args.connect_timeout <= 0:
        parser.error("connect-timeout 必須大於零")
    if args.max_message_mib is not None and not 1 <= args.max_message_mib <= 1024:
        parser.error("max-message-mib 必須介於 1 與 1024")
    try:
        script_args = json.loads(args.args_json)
    except json.JSONDecodeError as error:
        parser.error(f"args-json 不是有效 JSON：{error}")
    if not isinstance(script_args, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in script_args.items()
    ):
        parser.error("args-json 必須是字串鍵值的物件")
    if args.max_message_mib is not None:
        # 必須在匯入 PyAnsys 及建立客戶端之前設定，不影響現有 MCP 連線。
        os.environ["PYGEOMETRY_MAX_MESSAGE_LENGTH"] = str(args.max_message_mib * 1024 * 1024)
    try:
        from ansys.geometry.core import Modeler

        modeler = Modeler(
            host=args.host,
            port=args.port,
            transport_mode="insecure",
            timeout=args.connect_timeout,
        )
        values, _ = modeler.run_script_file(
            args.script.resolve(), script_args=script_args, import_design=False
        )
        print(json.dumps(values, ensure_ascii=False, indent=2))
        # 工作階段屬於使用者，不呼叫會關閉應用程式的 Modeler.close()。
    except Exception as error:
        print(f"原生腳本執行失敗：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
