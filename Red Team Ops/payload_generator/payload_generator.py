import argparse
import base64
import urllib.parse
from pathlib import Path


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def encode_base64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()


def encode_hex(data: str) -> str:
    return data.encode().hex()


def encode_url(data: str) -> str:
    return urllib.parse.quote(data)


def load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.exists():
        raise SystemExit(f"[!] Template not found: {path}")
    return path.read_text()


def generate_template(template_name: str, host: str | None, port: int | None) -> str:
    content = load_template(template_name)
    if host:
        content = content.replace("{{HOST}}", host)
    if port:
        content = content.replace("{{PORT}}", str(port))
    return content


def parse_args():
    parser = argparse.ArgumentParser(description="Payload Generator (Competition-Safe)")

    sub = parser.add_subparsers(dest="mode", required=True)

    enc = sub.add_parser("encode", help="Encode a string")
    enc.add_argument("type", choices=["base64", "hex", "url"], help="Encoding type")
    enc.add_argument("data", help="String to encode")

    temp = sub.add_parser("template", help="Generate a payload template")
    temp.add_argument("name", choices=["reverse_shell", "bof"], help="Template name")
    temp.add_argument("--host", help="Target host (optional)")
    temp.add_argument("--port", type=int, help="Target port (optional)")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == "encode":
        if args.type == "base64":
            print(encode_base64(args.data))
        elif args.type == "hex":
            print(encode_hex(args.data))
        elif args.type == "url":
            print(encode_url(args.data))

    elif args.mode == "template":
        name_map = {
            "reverse_shell": "reverse_shell_template.txt",
            "bof": "bof_template.txt",
        }
        template_file = name_map[args.name]
        output = generate_template(template_file, args.host, args.port)
        print(output)


if __name__ == "__main__":
    main()
