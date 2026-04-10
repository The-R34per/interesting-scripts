import argparse
import platform
from pathlib import Path
from datetime import datetime


def header(title):
    return f"{'=' * 10} {title} {'=' * 10}"

def explain(text, mode):
    if mode == "raw":
        return ""
    if mode == "explain":
        return f"Why this matters: {text}"
    if mode == "severity":
        return f"[MEDIUM] {text}"
    return ""

def safe_listdir(path):
    try:
        return list(Path(path).iterdir())
    except Exception:
        return []


def check_users(os_name, mode):
    lines = [header("User & Group Information")]
    lines.append("Current user: <placeholder>")
    lines.append("Groups: <placeholder>")
    lines.append(explain("Group membership affects privilege boundaries.", mode))
    lines.append("")
    return lines

def check_sudo_admin(os_name, mode):
    lines = [header("Sudo / Admin Surface")]
    lines.append("Sudo/admin configuration: <placeholder>")
    lines.append(explain("Misconfigurations here may allow privilege escalation.", mode))
    lines.append("")
    return lines

def check_services(os_name, mode):
    lines = [header("Service Configuration Surface")]
    lines.append("Service permissions: <placeholder>")
    lines.append(explain("Weak service configs can allow privilege escalation.", mode))
    lines.append("")
    return lines

def check_suid(os_name, mode):
    lines = [header("SUID / SGID (Linux Only)")]
    if os_name != "linux":
        lines.append("Skipped (not Linux).")
        lines.append("")
        return lines
    lines.append("SUID/SGID binaries: <placeholder>")
    lines.append(explain("SUID binaries may allow unintended privilege elevation.", mode))
    lines.append("")
    return lines

def check_path(os_name, mode):
    lines = [header("PATH & Writable Directories")]
    lines.append("PATH entries: <placeholder>")
    lines.append("Writable PATH entries: <placeholder>")
    lines.append(explain("Writable PATH entries can allow execution hijacking.", mode))
    lines.append("")
    return lines

def check_cron(os_name, mode):
    lines = [header("Cron / Scheduled Tasks")]
    lines.append("Cron/scheduled tasks: <placeholder>")
    lines.append(explain("Weak scheduled tasks can be hijacked for escalation.", mode))
    lines.append("")
    return lines

def check_containers(os_name, mode):
    lines = [header("Container / Virtualization Indicators")]
    lines.append("Container indicators: <placeholder>")
    lines.append(explain("Container breakout vectors may exist.", mode))
    lines.append("")
    return lines


def build_report(args):
    os_name = platform.system().lower()
    sections = []

    # Determine which modules to run
    selected = any([
        args.users, args.sudo, args.services, args.suid,
        args.path, args.cron, args.containers, args.all
    ])

    run_users = args.users or args.all or not selected
    run_sudo = args.sudo or args.all or not selected
    run_services = args.services or args.all or not selected
    run_suid = args.suid or args.all or not selected
    run_path = args.path or args.all or not selected
    run_cron = args.cron or args.all or not selected
    run_containers = args.containers or args.all or not selected

    # Banner
    sections.append(header("Privilege Escalation Surface Mapper"))
    sections.append(f"OS detected: {os_name}")
    sections.append(f"Timestamp: {datetime.now().isoformat()}Z")
    sections.append("Output mode: " + args.mode)
    sections.append("")

    if run_users:
        sections.extend(check_users(os_name, args.mode))
    if run_sudo:
        sections.extend(check_sudo_admin(os_name, args.mode))
    if run_services:
        sections.extend(check_services(os_name, args.mode))
    if run_suid:
        sections.extend(check_suid(os_name, args.mode))
    if run_path:
        sections.extend(check_path(os_name, args.mode))
    if run_cron:
        sections.extend(check_cron(os_name, args.mode))
    if run_containers:
        sections.extend(check_containers(os_name, args.mode))

    return "\n".join(sections)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Privilege Escalation Surface Mapper (Cyber Combat – Tool F)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Output style
    parser.add_argument(
        "--raw", action="store_const", const="raw", dest="mode",
        help="Findings only (no explanations)"
    )
    parser.add_argument(
        "--explain", action="store_const", const="explain", dest="mode",
        help="Findings + short notes (default)"
    )
    parser.add_argument(
        "--severity", action="store_const", const="severity", dest="mode",
        help="Findings + notes + severity tags"
    )
    parser.set_defaults(mode="explain")

    # Modules
    parser.add_argument("--users", action="store_true", help="User/group info")
    parser.add_argument("--sudo", action="store_true", help="Sudo/admin surface")
    parser.add_argument("--services", action="store_true", help="Service configs")
    parser.add_argument("--suid", action="store_true", help="SUID/SGID binaries (Linux)")
    parser.add_argument("--path", action="store_true", help="PATH & writable dirs")
    parser.add_argument("--cron", action="store_true", help="Cron/scheduled tasks")
    parser.add_argument("--containers", action="store_true", help="Container indicators")
    parser.add_argument("--all", action="store_true", help="Run all modules")

    parser.add_argument("-o", "--out", help="Save report to file", default=None)

    return parser.parse_args()

def main():
    args = parse_args()
    report = build_report(args)

    print(report)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n[+] Report saved to {args.out}")
        except Exception as e:
            print(f"[!] Failed to write report: {e}")

if __name__ == "__main__":
    main()
