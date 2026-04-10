#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import platform
import re
import shutil
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ------------------ Categorization ------------------


def categorize_file(path: str) -> str:
    name = os.path.basename(path).lower()

    # Memory artifacts
    if any(k in name for k in ["memory", "memdump", "mem_dump", "ramdump", "ram_dump"]) \
            or name.endswith((".dmp", ".raw")):
        return "Memory"

    # Network artifacts
    if any(k in name for k in ["network", "nmap", "scan", "pcap", "traffic"]) \
            or name.endswith((".pcap", ".pcapng")):
        return "Network"

    # IOC artifacts
    if "ioc" in name or "iocs" in name:
        return "IOCs"

    # Integrity / baseline artifacts
    if any(k in name for k in ["baseline", "integrity", "compare", "diff"]):
        return "Integrity"

    # Persistence artifacts
    if any(k in name for k in ["persist", "autoruns", "startup", "runkeys"]):
        return "Persistence"

    # Malware artifacts
    if any(k in name for k in ["malware", "sample", "payload"]) \
            or name.endswith((".exe", ".dll", ".scr", ".bin")):
        return "Malware"

    # Reports / logs
    if name.endswith((".txt", ".md", ".log")) or "report" in name:
        return "Reports"

    return "Other"


# ------------------ Stats helpers ------------------


IOC_TYPE_KEYS = {"type", "value"}
STATUS_KEY = "status"


def try_count_iocs(file_path: str) -> int:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except Exception:
        return 0

    if isinstance(data, list) and data and all(isinstance(x, dict) for x in data):
        if any(IOC_TYPE_KEYS.issubset(x.keys()) for x in data):
            return len(data)
    return 0


def try_count_integrity_statuses(file_path: str) -> dict:
    counts = defaultdict(int)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except Exception:
        return counts

    if isinstance(data, list) and data and all(isinstance(x, dict) for x in data):
        for item in data:
            status = item.get(STATUS_KEY)
            if isinstance(status, str):
                counts[status] += 1
    return counts


def try_count_network_indicators(file_path: str) -> dict:
    ip_re = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    domain_re = re.compile(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
    url_re = re.compile(r"\bhttps?://[^\s\"'<>]+")
    counts = {"ips": 0, "domains": 0, "urls": 0}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return counts

    counts["urls"] += len(url_re.findall(text))
    counts["ips"] += len(ip_re.findall(text))
    # crude domain count (may overlap with URLs)
    counts["domains"] += len(domain_re.findall(text))
    return counts


# ------------------ Core processing ------------------


def organize_artifacts(source: str, dest: str, verbose: bool = False):
    source = os.path.abspath(source)
    dest = os.path.abspath(dest)

    category_counts = defaultdict(int)
    ioc_total = 0
    integrity_status_counts = defaultdict(int)
    network_indicator_totals = {"ips": 0, "domains": 0, "urls": 0}

    for root, _dirs, files in os.walk(source):
        for fname in files:
            src_path = os.path.join(root, fname)
            rel_path = os.path.relpath(src_path, source)
            category = categorize_file(src_path)
            category_counts[category] += 1

            dest_dir = os.path.join(dest, category)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, fname)

            if verbose:
                print(f"[+] {rel_path} -> {category}/{fname}")

            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"[!] Failed to copy {src_path} -> {dest_path}: {e}", file=sys.stderr)
                continue

            # Stats enrichment
            if category == "IOCs" and fname.lower().endswith(".json"):
                ioc_total += try_count_iocs(src_path)
            elif category == "Integrity" and fname.lower().endswith(".json"):
                counts = try_count_integrity_statuses(src_path)
                for k, v in counts.items():
                    integrity_status_counts[k] += v
            elif category == "Network":
                net_counts = try_count_network_indicators(src_path)
                for k, v in net_counts.items():
                    network_indicator_totals[k] += v

    return {
        "category_counts": dict(category_counts),
        "ioc_total": ioc_total,
        "integrity_status_counts": dict(integrity_status_counts),
        "network_indicator_totals": network_indicator_totals,
    }


# ------------------ Report generation ------------------


def resolve_report_path(base: str, fmt: str) -> str:
    base_path = Path(base)
    ext = ".md" if fmt == "md" else ".txt"
    return str(base_path.with_suffix(ext))


def load_notes(notes_path: str | None) -> str:
    if not notes_path:
        return "<empty>"
    try:
        with open(notes_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
        return content if content else "<empty>"
    except Exception as e:
        return f"<failed to load notes: {e}>"


def generate_txt_report(stats: dict, analyst: str | None, notes: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    host = platform.node() or "unknown"

    lines = []
    lines.append("=" * 60)
    lines.append("CYBER COMBAT ARTIFACT REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {now}")
    lines.append(f"Analyst:   {analyst or 'unknown'}")
    lines.append(f"Host:      {host}")
    lines.append("")
    lines.append("Artifacts Collected:")
    for cat, count in sorted(stats["category_counts"].items()):
        lines.append(f"- {cat}: {count} file(s)")
    if not stats["category_counts"]:
        lines.append("- None")
    lines.append("")
    lines.append("Summary:")
    lines.append(f"- Total IOCs: {stats['ioc_total']}")
    if stats["integrity_status_counts"]:
        for k, v in sorted(stats["integrity_status_counts"].items()):
            lines.append(f"- Integrity {k}: {v}")
    if any(stats["network_indicator_totals"].values()):
        lines.append(f"- Network IPs: {stats['network_indicator_totals']['ips']}")
        lines.append(f"- Network Domains: {stats['network_indicator_totals']['domains']}")
        lines.append(f"- Network URLs: {stats['network_indicator_totals']['urls']}")
    lines.append("")
    lines.append("Notes:")
    lines.append(notes)
    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_md_report(stats: dict, analyst: str | None, notes: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    host = platform.node() or "unknown"

    lines = []
    lines.append("# Cyber Combat Artifact Report")
    lines.append("")
    lines.append(f"**Generated:** {now}  ")
    lines.append(f"**Analyst:** {analyst or 'unknown'}  ")
    lines.append(f"**Host:** {host}  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📁 Artifacts Collected")
    if stats["category_counts"]:
        for cat, count in sorted(stats["category_counts"].items()):
            lines.append(f"- **{cat}:** {count} file(s)")
    else:
        lines.append("- _None_")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Summary")
    lines.append(f"- **Total IOCs:** {stats['ioc_total']}")
    if stats["integrity_status_counts"]:
        for k, v in sorted(stats["integrity_status_counts"].items()):
            lines.append(f"- **Integrity {k}:** {v}")
    if any(stats["network_indicator_totals"].values()):
        lines.append(f"- **Network IPs:** {stats['network_indicator_totals']['ips']}")
        lines.append(f"- **Network Domains:** {stats['network_indicator_totals']['domains']}")
        lines.append(f"- **Network URLs:** {stats['network_indicator_totals']['urls']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📝 Notes")
    lines.append(notes)
    lines.append("")
    return "\n".join(lines)


def write_report(dest: str, report_base: str | None, fmt: str, stats: dict, analyst: str | None, notes_path: str | None):
    notes = load_notes(notes_path)
    if not report_base:
        report_base = os.path.join(dest, "artifact_report")

    report_path = resolve_report_path(report_base, fmt)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    if fmt == "md":
        content = generate_md_report(stats, analyst, notes)
    else:
        content = generate_txt_report(stats, analyst, notes)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Report written to {report_path}")


# ------------------ ZIP packaging ------------------


def create_zip(dest: str, zip_path: str):
    dest = os.path.abspath(dest)
    zip_path = os.path.abspath(zip_path)
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(dest):
            for fname in files:
                full_path = os.path.join(root, fname)
                arcname = os.path.relpath(full_path, dest)
                zf.write(full_path, arcname=arcname)
    print(f"[+] ZIP archive created at {zip_path}")


# ------------------ CLI ------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Artifact Packaging & Report Generator (Cyber Combat Utility)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    core = parser.add_argument_group("Core paths")
    core.add_argument("--source", required=True, help="Source directory containing tool outputs")
    core.add_argument("--dest", default="Artifacts", help="Destination directory for organized artifacts")

    out = parser.add_argument_group("Output options")
    out.add_argument("--zip", help="Create a ZIP archive of the destination directory")
    out.add_argument("--report", help="Path (without or with extension) for the summary report")
    out.add_argument(
        "--report-format",
        choices=["txt", "md"],
        default="txt",
        help="Report format (plain text or Markdown)",
    )
    out.add_argument("--analyst", help="Analyst name to embed in the report")
    out.add_argument("--notes", help="Optional notes file to include in the report")

    misc = parser.add_argument_group("Behavior")
    misc.add_argument("--clean", action="store_true", help="Remove destination directory before rebuilding")
    misc.add_argument("--verbose", action="store_true", help="Show detailed processing output")

    return parser.parse_args()


def main():
    args = parse_args()

    source = args.source
    dest = args.dest

    if not os.path.isdir(source):
        print(f"[!] Source directory does not exist: {source}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(dest) and args.clean:
        try:
            shutil.rmtree(dest)
            print(f"[+] Cleaned existing destination: {dest}")
        except Exception as e:
            print(f"[!] Failed to clean destination {dest}: {e}", file=sys.stderr)
            sys.exit(1)

    os.makedirs(dest, exist_ok=True)

    print(f"[+] Organizing artifacts from {source} -> {dest}")
    stats = organize_artifacts(source, dest, verbose=args.verbose)

    # Always generate a report, even if user didn't specify --report
    write_report(
        dest=dest,
        report_base=args.report,
        fmt=args.report_format,
        stats=stats,
        analyst=args.analyst,
        notes_path=args.notes,
    )

    if args.zip:
        create_zip(dest, args.zip)


if __name__ == "__main__":
    main()
