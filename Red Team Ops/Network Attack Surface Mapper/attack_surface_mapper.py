import argparse
import asyncio
import socket
from contextlib import closing
from datetime import datetime

COMMON_PORTS = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    139: "netbios",
    143: "imap",
    443: "https",
    445: "smb",
    3389: "rdp",
}


def risk_score(port: int, banner: str | None) -> int:
    score = 0

    if port in (21, 23, 25, 80, 110, 139, 143, 445, 3389):
        score += 3
    if port in (22, 53, 443):
        score += 2

    if banner:
        b = banner.lower()
        if "openssh" in b:
            score += 1
        if "apache" in b or "nginx" in b or "iis" in b:
            score += 2
        if "ftp" in b and "anonymous" in b:
            score += 3
        if "smb" in b or "samba" in b:
            score += 2

    return score


async def grab_banner(host: str, port: int, timeout: float = 1.0) -> str | None:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
    except Exception:
        return None

    banner = None
    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
        if data:
            banner = data.decode(errors="ignore").strip()
    except Exception:
        pass

    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass

    return banner


async def scan_port(host: str, port: int, timeout: float = 0.5) -> dict | None:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(timeout)
        try:
            result = s.connect_ex((host, port))
        except Exception:
            return None

        if result != 0:
            return None

    banner = await grab_banner(host, port)
    service = COMMON_PORTS.get(port, "unknown")
    score = risk_score(port, banner)

    return {
        "port": port,
        "service": service,
        "banner": banner,
        "risk": score,
    }


async def scan_host(host: str, ports: list[int], concurrency: int = 200):
    sem = asyncio.Semaphore(concurrency)
    results = []

    async def worker(p: int):
        async with sem:
            r = await scan_port(host, p)
            if r:
                results.append(r)

    tasks = [asyncio.create_task(worker(p)) for p in ports]
    await asyncio.gather(*tasks)
    return results


def parse_ports(port_str: str) -> list[int]:
    ports: list[int] = []
    parts = port_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def print_report(host: str, findings: list[dict]):
    print("\n=== Attack Surface Report ===")
    print(f"Host: {host}")
    print(f"Scanned at (UTC): {datetime.now()}")

    if not findings:
        print("\nNo open ports found in the scanned range.")
        return

    findings.sort(key=lambda x: x["risk"], reverse=True)

    print("\nOpen Ports (sorted by risk):\n")
    print(f"{'PORT':<6} {'SERVICE':<10} {'RISK':<4} BANNER")
    print("-" * 80)
    for f in findings:
        banner = f["banner"] or ""
        if len(banner) > 60:
            banner = banner[:57] + "..."
        print(f"{f['port']:<6} {f['service']:<10} {f['risk']:<4} {banner}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Network Attack Surface Mapper"
    )
    parser.add_argument("host", help="Target host/IP")
    parser.add_argument(
        "-p",
        "--ports",
        default="1-1024",
        help="Ports to scan (e.g. '1-1024', '22,80,443', '1-1024,3389')",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ports = parse_ports(args.ports)

    print(f"[+] Scanning host: {args.host}")
    print(f"[+] Ports: {ports[0]}-{ports[-1]} (or custom list)")
    findings = asyncio.run(scan_host(args.host, ports))
    print_report(args.host, findings)


if __name__ == "__main__":
    main()
