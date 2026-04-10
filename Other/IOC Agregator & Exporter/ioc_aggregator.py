#!/usr/bin/env python3
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List


# ------------------ IOC store ------------------


class IOCStore:
    def __init__(self):
        # type -> value -> set(sources)
        self.data: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))

    def add(self, ioc_type: str, value: str, source: str = ""):
        t = normalize_type(ioc_type)
        if not t:
            return
        v = normalize_value(t, value)
        if not v:
            return
        if source:
            self.data[t][v].add(source)
        else:
            self.data[t][v].add("unknown")

    def types(self):
        return sorted(self.data.keys())

    def items(self, only_type: str = None):
        if only_type:
            t = normalize_type(only_type)
            if not t or t not in self.data:
                return []
            return [(t, v, self.data[t][v]) for v in sorted(self.data[t].keys())]
        out = []
        for t in sorted(self.data.keys()):
            for v in sorted(self.data[t].keys()):
                out.append((t, v, self.data[t][v]))
        return out

    def counts(self, only_type: str = None):
        if only_type:
            t = normalize_type(only_type)
            if not t or t not in self.data:
                return {t: 0}
            return {t: len(self.data[t])}
        return {t: len(self.data[t]) for t in self.data.keys()}


# ------------------ Normalization ------------------


TYPE_MAP = {
    "hash": "hash",
    "hashes": "hash",
    "md5": "hash",
    "sha1": "hash",
    "sha256": "hash",
    "ip": "ip",
    "ips": "ip",
    "ipaddress": "ip",
    "domain": "domain",
    "domains": "domain",
    "hostname": "domain",
    "host": "domain",
    "url": "url",
    "urls": "url",
    "uri": "url",
    "file": "file",
    "files": "file",
    "filepath": "file",
    "path": "file",
    "registry": "registry",
    "reg": "registry",
    "registry_key": "registry",
    "registrykey": "registry",
}


def normalize_type(t: str) -> str:
    if not t:
        return ""
    t = t.strip().lower()
    return TYPE_MAP.get(t, t if t in {"hash", "ip", "domain", "url", "file", "registry"} else "")


def normalize_value(t: str, v: str) -> str:
    if not v:
        return ""
    v = v.strip()
    if not v:
        return ""
    if t in {"hash", "domain"}:
        return v.lower()
    if t == "url":
        return v.strip(".,;\"'()")
    return v


# ------------------ Regex extraction from text ------------------


IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HASH32_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
HASH40_RE = re.compile(r"\b[a-fA-F0-9]{40}\b")
HASH64_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
DOMAIN_RE = re.compile(r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
URL_RE = re.compile(r"\bhttps?://[^\s\"'<>]+")
REG_RE = re.compile(r"\bHKEY_[A-Z0-9_\\]

+\

\[^\s]+", re.IGNORECASE)
FILE_RE = re.compile(r"\b[^\s\"']+[\\/][^\s\"']+\.[A-Za-z0-9]{2,4}\b")


def valid_ip(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def extract_iocs_from_text(path: str, store: IOCStore, label: str = ""):
    p = Path(path)
    if not p.is_file():
        print(f"[!] Text file not found: {path}", file=sys.stderr)
        return
    source_base = p.name
    source = f"{label}:{source_base}" if label else source_base

    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[!] Failed to read text file {path}: {e}", file=sys.stderr)
        return

    # URLs
    for m in URL_RE.findall(text):
        store.add("url", m, source)

    # IPs
    for m in IP_RE.findall(text):
        if valid_ip(m):
            store.add("ip", m, source)

    # Hashes
    for m in HASH32_RE.findall(text):
        store.add("hash", m, source)
    for m in HASH40_RE.findall(text):
        store.add("hash", m, source)
    for m in HASH64_RE.findall(text):
        store.add("hash", m, source)

    # Domains (avoid ones that are just IPs)
    for m in DOMAIN_RE.findall(text):
        if valid_ip(m):
            continue
        store.add("domain", m, source)

    # Registry keys
    for m in REG_RE.findall(text):
        store.add("registry", m, source)

    # File paths
    for m in FILE_RE.findall(text):
        store.add("file", m, source)


# ------------------ JSON / CSV loaders ------------------


def load_from_json(path: str, store: IOCStore, label: str = ""):
    p = Path(path)
    if not p.is_file():
        print(f"[!] JSON file not found: {path}", file=sys.stderr)
        return
    source_base = p.name
    base_source = f"{label}:{source_base}" if label else source_base

    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        print(f"[!] Failed to read JSON {path}: {e}", file=sys.stderr)
        return

    if not isinstance(data, list):
        print(f"[!] JSON must be a list of IOC objects: {path}", file=sys.stderr)
        return

    for item in data:
        if not isinstance(item, dict):
            continue
        t = item.get("type", "")
        v = item.get("value", "")
        src = item.get("source", "") or base_source
        if label:
            src = f"{label}:{src}"
        store.add(t, v, src)


def load_from_csv(path: str, store: IOCStore, label: str = ""):
    p = Path(path)
    if not p.is_file():
        print(f"[!] CSV file not found: {path}", file=sys.stderr)
        return
    source_base = p.name

    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = row.get("type") or row.get("Type") or ""
                v = row.get("value") or row.get("Value") or ""
                src = row.get("source") or row.get("Source") or source_base
                if label:
                    src = f"{label}:{src}"
                store.add(t, v, src)
    except Exception as e:
        print(f"[!] Failed to read CSV {path}: {e}", file=sys.stderr)


# ------------------ Reporting ------------------


def header(title: str) -> str:
    return f"{'=' * 10} {title} {'=' * 10}"


def summarize(store: IOCStore, only_type: str = None) -> str:
    counts = store.counts(only_type)
    lines: List[str] = []
    lines.append(header("IOC Summary"))
    if not counts:
        lines.append("No IOCs collected.")
        lines.append("")
        return "\n".join(lines)

    order = ["hash", "ip", "domain", "url", "file", "registry"]
    for t in order:
        if t in counts:
            lines.append(f"{t.capitalize()}s: {counts[t]}")
    for t in counts:
        if t not in order:
            lines.append(f"{t}: {counts[t]}")
    lines.append("")
    return "\n".join(lines)


def format_text_listing(store: IOCStore, only_type: str = None) -> str:
    lines: List[str] = []
    items = store.items(only_type)
    if not items:
        lines.append(header("IOC Listing"))
        lines.append("No IOCs to display.")
        lines.append("")
        return "\n".join(lines)

    grouped: Dict[str, List[str]] = defaultdict(list)
    for t, v, _sources in items:
        grouped[t].append(v)

    for t in sorted(grouped.keys()):
        lines.append(header(f"{t.capitalize()}s"))
        for v in grouped[t]:
            lines.append(v)
        lines.append("")

    return "\n".join(lines)


def write_text_file(store: IOCStore, path: str, only_type: str = None):
    content = format_text_listing(store, only_type)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Text IOC list written to {path}")
    except Exception as e:
        print(f"[!] Failed to write text IOC file {path}: {e}", file=sys.stderr)


def write_csv_file(store: IOCStore, path: str, only_type: str = None):
    items = store.items(only_type)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "value", "source"])
            for t, v, sources in items:
                if not sources:
                    writer.writerow([t, v, "unknown"])
                else:
                    for s in sorted(sources):
                        writer.writerow([t, v, s])
        print(f"[+] CSV IOC list written to {path}")
    except Exception as e:
        print(f"[!] Failed to write CSV IOC file {path}: {e}", file=sys.stderr)


def write_json_file(store: IOCStore, path: str, only_type: str = None):
    items = store.items(only_type)
    out = []
    for t, v, sources in items:
        out.append({
            "type": t,
            "value": v,
            "sources": sorted(list(sources)) if sources else []
        })
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"[+] JSON IOC list written to {path}")
    except Exception as e:
        print(f"[!] Failed to write JSON IOC file {path}: {e}", file=sys.stderr)


# ------------------ CLI ------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="IOC Aggregator & Exporter (Cyber Combat – Tool J)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    src = parser.add_argument_group("Inputs")
    src.add_argument("--from-text", action="append", help="Free-form text file to extract IOCs from")
    src.add_argument("--from-json", action="append", help="JSON IOC file (list of {type,value,source})")
    src.add_argument("--from-csv", action="append", help="CSV IOC file (type,value,source)")

    parser.add_argument("--label", help="Optional label to tag IOCs from this run")

    filt = parser.add_argument_group("Filtering")
    filt.add_argument(
        "--only",
        help="Only include a specific IOC type (e.g., hashes, ips, domains, urls, files, registry)",
    )
    filt.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, no detailed listing",
    )

    out = parser.add_argument_group("Outputs")
    out.add_argument("--out-text", help="Write IOC list to a text file")
    out.add_argument("--out-csv", help="Write IOC list to a CSV file")
    out.add_argument("--out-json", help="Write IOC list to a JSON file")

    return parser.parse_args()


def main():
    args = parse_args()
    store = IOCStore()

    if not args.from_text and not args.from_json and not args.from_csv:
        print("[!] No input files provided.", file=sys.stderr)
        print("    Use one or more of:", file=sys.stderr)
        print("      --from-text FILE", file=sys.stderr)
        print("      --from-json FILE", file=sys.stderr)
        print("      --from-csv FILE", file=sys.stderr)
        sys.exit(1)

    label = args.label or ""

    # Load from text
    if args.from_text:
        for path in args.from_text:
            extract_iocs_from_text(path, store, label)

    # Load from JSON
    if args.from_json:
        for path in args.from_json:
            load_from_json(path, store, label)

    # Load from CSV
    if args.from_csv:
        for path in args.from_csv:
            load_from_csv(path, store, label)

    # If nothing collected, bail
    if not store.data:
        print("[!] No IOCs collected from the provided inputs.", file=sys.stderr)
        sys.exit(1)

    only_type = args.only

    # Console output
    summary = summarize(store, only_type)
    print(summary)

    if not args.summary_only:
        listing = format_text_listing(store, only_type)
        print(listing)

    # Files
    if args.out_text:
        write_text_file(store, args.out_text, only_type)
    if args.out_csv:
        write_csv_file(store, args.out_csv, only_type)
    if args.out_json:
        write_json_file(store, args.out_json, only_type)


if __name__ == "__main__":
    main()
