import argparse
from datetime import datetime, timedelta
from pathlib import Path
import csv
import sys


def load_list_from_file_or_arg(file_arg, inline_arg, label):
    items = []

    if file_arg:
        p = Path(file_arg)
        if not p.is_file():
            print(f"[!] {label} file not found: {file_arg}", file=sys.stderr)
            return []
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        items.append(line)
        except Exception as e:
            print(f"[!] Failed to read {label} file {file_arg}: {e}", file=sys.stderr)
            return []

    if inline_arg:
        for part in inline_arg.split(","):
            part = part.strip()
            if part:
                items.append(part)

    return list(dict.fromkeys(items))  # dedupe, preserve order


def header(title):
    return f"{'=' * 10} {title} {'=' * 10}"


def build_schedule(users, passwords, lockout_threshold, lockout_window_min,
                   cooldown_min, per_round, max_attempts_per_user):

    schedule = []
    now = datetime.now()
    lockout_window = timedelta(minutes=lockout_window_min)
    cooldown = timedelta(minutes=cooldown_min)

    rounds = []
    for i in range(0, len(passwords), per_round):
        rounds.append(passwords[i:i + per_round])

    attempts_per_user = {u: 0 for u in users}

    current_round_start = now
    round_number = 1

    for round_passwords in rounds:
        attempts_in_round = []
        for pwd in round_passwords:
            for user in users:
                if attempts_per_user[user] >= max_attempts_per_user:
                    continue
                attempts_in_round.append((user, pwd))

        if not attempts_in_round:
            break

        total_attempts = len(attempts_in_round)
        if total_attempts == 1:
            step = timedelta(0)
        else:
            step = lockout_window / max(total_attempts - 1, 1)

        for idx, (user, pwd) in enumerate(attempts_in_round):
            ts = current_round_start + step * idx
            attempts_per_user[user] += 1
            schedule.append({
                "round": round_number,
                "timestamp": ts,
                "user": user,
                "password": pwd,
            })

        current_round_start = current_round_start + lockout_window + cooldown
        round_number += 1

    return schedule, attempts_per_user


def summarize_plan(schedule, attempts_per_user, lockout_threshold, lockout_window_min):
    total_attempts = len(schedule)
    max_attempts = max(attempts_per_user.values()) if attempts_per_user else 0
    risk = "NONE"
    if max_attempts > lockout_threshold:
        risk = "HIGH"
    elif max_attempts == lockout_threshold:
        risk = "ELEVATED"

    summary_lines = []
    summary_lines.append(header("Plan Summary"))
    summary_lines.append(f"Total attempts: {total_attempts}")
    summary_lines.append(f"Users involved: {len(attempts_per_user)}")
    summary_lines.append(f"Lockout threshold: {lockout_threshold} attempts per {lockout_window_min} minutes")
    summary_lines.append(f"Max attempts per user in this plan: {max_attempts}")
    summary_lines.append(f"Estimated lockout risk: {risk}")
    summary_lines.append("")
    summary_lines.append("Per-user attempt counts:")
    for user, count in attempts_per_user.items():
        summary_lines.append(f"  {user}: {count}")
    summary_lines.append("")
    return "\n".join(summary_lines)


def format_schedule_text(schedule):
    lines = []
    lines.append(header("Credential Spray Plan (Simulated)"))
    lines.append("NOTE: This is a planning tool only. No authentication is performed.")
    lines.append("")
    lines.append(f"{'Round':<6} {'Timestamp':<20} {'User':<20} Password")
    lines.append("-" * 80)
    for entry in schedule:
        ts_str = entry["timestamp"].strftime("%Y-%m-%d %H:%M")
        lines.append(f"{entry['round']:<6} {ts_str:<20} {entry['user']:<20} {entry['password']}")
    lines.append("")
    return "\n".join(lines)


def write_csv(schedule, csv_path):
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["round", "timestamp", "user", "password"])
            for entry in schedule:
                writer.writerow([
                    entry["round"],
                    entry["timestamp"].isoformat(timespec="minutes"),
                    entry["user"],
                    entry["password"],
                ])
        print(f"[+] CSV plan written to {csv_path}")
    except Exception as e:
        print(f"[!] Failed to write CSV file {csv_path}: {e}", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Credential Spray Automator (Safe Planner – Cyber Combat Tool)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--users", help="File with one username per line")
    parser.add_argument("--user", help="Comma-separated list of usernames")
    parser.add_argument("--passwords", help="File with one password per line")
    parser.add_argument("--password", help="Comma-separated list of passwords")

    parser.add_argument("--lockout-threshold", type=int, default=5,
                        help="Max attempts per user before lockout")
    parser.add_argument("--lockout-window", type=int, default=15,
                        help="Lockout window in minutes")
    parser.add_argument("--cooldown", type=int, default=30,
                        help="Cooldown between rounds in minutes")

    parser.add_argument("--per-round", type=int, default=1,
                        help="Passwords per round")
    parser.add_argument("--max-attempts-per-user", type=int, default=3,
                        help="Maximum attempts per user in the entire plan")

    parser.add_argument("-o", "--out", help="Write text plan to this file")
    parser.add_argument("--csv", help="Write CSV plan to this file")
    parser.add_argument("--summary-only", action="store_true",
                        help="Only print summary, not full schedule")

    return parser.parse_args()


def main():
    args = parse_args()

    users = load_list_from_file_or_arg(args.users, args.user, "Users")
    passwords = load_list_from_file_or_arg(args.passwords, args.password, "Passwords")

    if not users:
        print("[!] No users provided. Use --users FILE or --user u1,u2,...", file=sys.stderr)
        sys.exit(1)
    if not passwords:
        print("[!] No passwords provided. Use --passwords FILE or --password p1,p2,...", file=sys.stderr)
        sys.exit(1)

    schedule, attempts_per_user = build_schedule(
        users=users,
        passwords=passwords,
        lockout_threshold=args.lockout_threshold,
        lockout_window_min=args.lockout_window,
        cooldown_min=args.cooldown,
        per_round=args.per_round,
        max_attempts_per_user=args.max_attempts_per_user,
    )

    summary_text = summarize_plan(
        schedule,
        attempts_per_user,
        args.lockout_threshold,
        args.lockout_window,
    )

    if not args.summary_only:
        schedule_text = format_schedule_text(schedule)
        full_text = schedule_text + "\n" + summary_text
    else:
        full_text = summary_text

    print(full_text)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"\n[+] Plan written to {args.out}")
        except Exception as e:
            print(f"[!] Failed to write plan to {args.out}: {e}", file=sys.stderr)

    if args.csv:
        write_csv(schedule, args.csv)


if __name__ == "__main__":
    main()
