#!/usr/bin/env python3
import argparse
import time
from collections import Counter, defaultdict

import psutil


# ------------- helpers -------------

def header(title):
    return f"{'=' * 10} {title} {'=' * 10}"


def get_connections(kind="inet"):
    try:
        return psutil.net_connections(kind=kind)
    except Exception:
        return []


def format_conn(c, show_proc=True):
    laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "?:?"
    raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-:-"
    status = c.status
    proto = "TCP" if c.type == psutil.SOCK_STREAM else "UDP"
    pid = c.pid or 0
    pname = "unknown"
    if show_proc and pid:
        try:
            pname = psutil.Process(pid).name()
        except Exception:
            pname = "unknown"
    return proto, laddr, raddr, status, pid, pname


def filter_conn(c, args):
    if args.tcp and c.type != psutil.SOCK_STREAM:
        return False
    if args.udp and c.type != psutil.SOCK_DGRAM:
        return False
    if args.listening and c.status != psutil.CONN_LISTEN:
        return False
    if args.established and c.status != psutil.CONN_ESTABLISHED:
        return False
    return True


def analyze_suspicious(conns):
    alerts = []
    # count connections per (pid, raddr_ip)
    counter = Counter()
    proc_conn_count = Counter()
    for c in conns:
        if not c.raddr:
            continue
        key = (c.pid, c.raddr.ip)
        counter[key] += 1
        proc_conn_count[c.pid] += 1

    # beacon-like behavior
    for (pid, ip), count in counter.items():
        if count >= 10 and ip not in ("127.0.0.1", "0.0.0.0"):
            alerts.append(f"[Beacon?] PID {pid} has {count} connections to {ip}")

    # processes with many connections
    for pid, count in proc_conn_count.items():
        if count >= 20:
            alerts.append(f"[High conn count] PID {pid} has {count} active connections")

    # suspicious ports
    for c in conns:
        if not c.raddr:
            continue
        port = c.raddr.port
        if port in (4444, 1337, 2222) or port > 50000:
            alerts.append(
                f"[Suspicious port] PID {c.pid} -> {c.raddr.ip}:{port} ({c.status})"
            )

    return alerts


def snapshot(args):
    conns = [c for c in get_connections("inet") if filter_conn(c, args)]
    lines = []

    lines.append(header("Network Connections Snapshot"))
    lines.append(f"Total connections (after filters): {len(conns)}")
    lines.append("")
    lines.append(f"{'Proto':<5} {'Local':<22} {'Remote':<22} {'State':<13} {'PID':<6} Process")
    lines.append("-" * 80)

    for c in conns:
        proto, laddr, raddr, status, pid, pname = format_conn(c, show_proc=args.processes)
        lines.append(f"{proto:<5} {laddr:<22} {raddr:<22} {status:<13} {pid:<6} {pname}")

    lines.append("")
    lines.append(header("Alerts"))
    alerts = analyze_suspicious(conns)
    if alerts:
        lines.extend(alerts)
    else:
        lines.append("No obvious suspicious patterns detected.")
    lines.append("")

    return "\n".join(lines)


def live_mode(args):
    prev_keys = set()
    interval = args.interval
    while True:
        conns = [c for c in get_connections("inet") if filter_conn(c, args)]
        current_keys = set(
            (c.type, c.laddr, c.raddr, c.status, c.pid) for c in conns
        )

        new_conns = current_keys - prev_keys
        closed_conns = prev_keys - current_keys

        print("\033[2J\033[H", end="")  # clear screen
        print(header("Live Network Activity"))
        print(f"Total connections (after filters): {len(conns)}")
        print(f"Interval: {interval}s")
        print("")
        print(f"{'Proto':<5} {'Local':<22} {'Remote':<22} {'State':<13} {'PID':<6} Process")
        print("-" * 80)

        for c in conns:
            proto, laddr, raddr, status, pid, pname = format_conn(c, show_proc=args.processes)
            print(f"{proto:<5} {laddr:<22} {raddr:<22} {status:<13} {pid:<6} {pname}")

        print("")
        print(header("Changes Since Last Interval"))
        if new_conns:
            print(f"[+] New connections: {len(new_conns)}")
        if closed_conns:
            print(f"[-] Closed connections: {len(closed_conns)}")
        if not new_conns and not closed_conns:
            print("No connection changes detected.")

        print("")
        print(header("Alerts"))
        alerts = analyze_suspicious(conns)
        if alerts:
            for a in alerts:
                print(a)
        else:
            print("No obvious suspicious patterns detected.")

        if args.out:
            try:
                with open(args.out, "a", encoding="utf-8") as f:
                    f.write(snapshot(args))
                    f.write("\n" + "=" * 80 + "\n")
            except Exception as e:
                print(f"[!] Failed to write to {args.out}: {e}")

        prev_keys = current_keys
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[+] Live monitoring stopped by user.")
            break


# ------------- CLI -------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Live Network Activity Analyzer (Cyber Combat – Tool E)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in continuous live mode",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Refresh interval in seconds for live mode",
    )
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Show TCP connections only",
    )
    parser.add_argument(
        "--udp",
        action="store_true",
        help="Show UDP connections only",
    )
    parser.add_argument(
        "--listening",
        action="store_true",
        help="Show listening ports only",
    )
    parser.add_argument(
        "--established",
        action="store_true",
        help="Show established connections only",
    )
    parser.add_argument(
        "--processes",
        dest="processes",
        action="store_true",
        help="Include process names (default)",
    )
    parser.add_argument(
        "--no-processes",
        dest="processes",
        action="store_false",
        help="Do not include process names",
    )
    parser.set_defaults(processes=True)

    parser.add_argument(
        "-o",
        "--out",
        help="Also write snapshot/live data to this file",
        default=None,
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.live:
        live_mode(args)
    else:
        report = snapshot(args)
        print(report)
        if args.out:
            try:
                with open(args.out, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"\n[+] Snapshot written to {args.out}")
            except Exception as e:
                print(f"[!] Failed to write snapshot to {args.out}: {e}")


if __name__ == "__main__":
    main()
