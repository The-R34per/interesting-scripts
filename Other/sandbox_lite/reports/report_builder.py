class ReportBuilder:
    def __init__(self, target, fs_events, proc_events, net_events, runtime):
        self.target = target
        self.fs_events = fs_events
        self.proc_events = proc_events
        self.net_events = net_events
        self.runtime = runtime

    def build(self):
        out = []
        out.append("=== Malware Sandbox Lite Report ===")
        out.append(f"Target: {self.target}")
        out.append(f"Runtime: {self.runtime:.2f} seconds")
        out.append("")

        out.append("=== File System Events ===")
        out.extend(self.fs_events or ["(none)"])
        out.append("")

        out.append("=== Process Events ===")
        out.extend(self.proc_events or ["(none)"])
        out.append("")

        out.append("=== Network Events ===")
        out.extend(self.net_events or ["(none)"])
        out.append("")

        return "\n".join(out)
