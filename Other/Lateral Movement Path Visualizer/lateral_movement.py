#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import csv
from collections import defaultdict

# ------------------ Helpers ------------------


def header(title):
    return f"{'=' * 10} {title} {'=' * 10}"


def load_hosts(path):
    hosts = []
    if not path:
        return hosts
    p = Path(path)
    if not p.is_file():
        print(f"[!] Hosts file not found: {path}", file=sys.stderr)
        return hosts
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    hosts.append(line)
    except Exception as e:
        print(f"[!] Failed to read hosts file {path}: {e}", file=sys.stderr)
    return list(dict.fromkeys(hosts))


def load_users(path):
    """
    users.txt format:
        HOST,USER
    """
    host_users = defaultdict(set)
    if not path:
        return host_users
    p = Path(path)
    if not p.is_file():
        print(f"[!] Users file not found: {path}", file=sys.stderr)
        return host_users
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [x.strip() for x in line.split(",")]
                if len(parts) < 2:
                    continue
                host, user = parts[0], parts[1]
                if host and user:
                    host_users[host].add(user)
    except Exception as e:
        print(f"[!] Failed to read users file {path}: {e}", file=sys.stderr)
    return host_users


def load_shares(path):
    """
    shares.txt format:
        HOST,SHARE,ACCESS
    """
    host_shares = defaultdict(list)
    if not path:
        return host_shares
    p = Path(path)
    if not p.is_file():
        print(f"[!] Shares file not found: {path}", file=sys.stderr)
        return host_shares
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [x.strip() for x in line.split(",")]
                if len(parts) < 2:
                    continue
                host = parts[0]
                share = parts[1]
                access = parts[2] if len(parts) > 2 else "unknown"
                if host and share:
                    host_shares[host].append((share, access))
    except Exception as e:
        print(f"[!] Failed to read shares file {path}: {e}", file=sys.stderr)
    return host_shares


# ------------------ Core Logic ------------------


def infer_edges(hosts, host_users, host_shares):
    """
    Build host-to-host edges based on:
    - Shared users across hosts (via_type='user')
    - Shares on a host that other hosts could potentially reach (via_type='share')
    """
    edges = set()

    # Shared users → potential credential reuse paths
    user_hosts = defaultdict(set)
    for host, users in host_users.items():
        for u in users:
            user_hosts[u].add(host)

    for user, hset in user_hosts.items():
        hlist = sorted(hset)
        for i in range(len(hlist)):
            for j in range(i + 1, len(hlist)):
                h1, h2 = hlist[i], hlist[j]
                edges.add((h1, h2, "user", user))
                edges.add((h2, h1, "user", user))

    # Shares → potential file-based pivot paths
    # Simple model: any other host in the hosts list could potentially reach the share host.
    for share_host, shares in host_shares.items():
        for share_name, access in shares:
            for src_host in hosts:
                if src_host == share_host:
                    continue
                via_value = f"{share_name} ({access})"
                edges.add((src_host, share_host, "share", via_value))

    return edges


def build_adjacency(edges):
    adjacency = defaultdict(list)
    for src, dst, via_type, via_value in edges:
        adjacency[src].append((dst, via_type, via_value))
    return adjacency


def summarize(hosts, host_users, host_shares, edges):
    lines = []
    lines.append(header("Summary"))
    lines.append(f"Total hosts: {len(hosts)}")
    lines.append(f"Total users (unique): {len({u for us in host_users.values() for u in us})}")
    lines.append(f"Total shares (host/share entries): {sum(len(v) for v in host_shares.values())}")
    lines.append(f"Total inferred lateral paths (edges): {len(edges)}")
    lines.append("")
    return "\n".join(lines)


def format_paths(edges):
    lines = []
    lines.append(header("Inferred Lateral Movement Paths (Path-Centric View)"))
    if not edges:
        lines.append("No lateral paths inferred from the provided data.")
        lines.append("")
        return "\n".join(lines)

    # Sort for stable output
    for src, dst, via_type, via_value in sorted(edges):
        if via_type == "user":
            lines.append(f"{src} -> {dst} via shared user '{via_value}'")
        elif via_type == "share":
            lines.append(f"{src} -> {dst} via share on {dst}: '{via_value}'")
        else:
            lines.append(f"{src} -> {dst} via {via_type}: {via_value}")
    lines.append("")
    return "\n".join(lines)


def format_adjacency(adjacency):
    lines = []
    lines.append(header("Host Adjacency (Graph-Centric View)"))
    if not adjacency:
        lines.append("No adjacency relationships inferred.")
        lines.append("")
        return "\n".join(lines)

    for host in sorted(adjacency.keys()):
        neighbors = adjacency[host]
        if not neighbors:
            continue
        lines.append(f"{host}:")
        for dst, via_type, via_value in sorted(neighbors):
            if via_type == "user":
                lines.append(f"  -> {dst} (shared user: {via_value})")
            elif via_type == "share":
                lines.append(f"  -> {dst} (share: {via_value})")
            else:
                lines.append(f"  -> {dst} ({via_type}: {via_value})")
        lines.append("")
    lines.append("")
    return "\n".join(lines)


def write_edges_csv(edges, path):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_host", "target_host", "via_type", "via_value"])
            for src, dst, via_type, via_value in sorted(edges):
                writer.writerow([src, dst, via_type, via_value])
        print(f"[+] Edge list written to {path}")
    except Exception as e:
        print(f"[!] Failed to write edges CSV {path}: {e}", file=sys.stderr)


# ------------------ CLI ------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Lateral Movement Path Visualizer (Cyber Combat – Tool H)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--hosts", help="File with one host per line")
    parser.add_argument("--users", help="File with HOST,USER per line")
    parser.add_argument("--shares", help="File with HOST,SHARE,ACCESS per line")

    parser.add_argument("--summary-only", action="store_true",
                        help="Only print summary, not full path/adjacency views")

    parser.add_argument("-o", "--out", help="Write full report to this file")
    parser.add_argument("--edges", help="Write edge list CSV to this file")

    return parser.parse_args()


def main():
    args = parse_args()

    hosts = load_hosts(args.hosts)
    host_users = load_users(args.users)
    host_shares = load_shares(args.shares)

    if not hosts and not host_users and not host_shares:
        print("[!] No input data provided. Use --hosts, --users, and/or --shares.", file=sys.stderr)
        sys.exit(1)

    # If hosts list is empty but users/shares reference hosts, infer hosts from those
    if not hosts:
        inferred_hosts = set(host_users.keys()) | set(host_shares.keys())
        hosts = sorted(inferred_hosts)

    edges = infer_edges(hosts, host_users, host_shares)
    adjacency = build_adjacency(edges)

    summary_text = summarize(hosts, host_users, host_shares, edges)

    if args.summary_only:
        report = summary_text
    else:
        paths_text = format_paths(edges)
        adjacency_text = format_adjacency(adjacency)
        report = summary_text + "\n" + paths_text + "\n" + adjacency_text

    print(report)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n[+] Report written to {args.out}")
        except Exception as e:
            print(f"[!] Failed to write report to {args.out}: {e}", file=sys.stderr)

    if args.edges:
        write_edges_csv(edges, args.edges)


if __name__ == "__main__":
    main()
