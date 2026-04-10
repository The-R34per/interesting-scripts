import os
import sys
import hashlib
import fnmatch
import time
import json
import argparse
from stat import S_ISDIR

IGNORE_PATTERNS = [
    "__pycache__",
    "*.log",
    "*.tmp",
    ".git",
    "venv",
    "node_modules",
]


def should_ignore(path):
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(path, pattern):
            return True
        if pattern in path.replace("\\", "/"):
            return True
    return False


def calculate_hash(file_path, algorithm="sha256"):
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        print(f"Unsupported algorithm: {algorithm}")
        return None

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hash_obj.update(data)

    return hash_obj.hexdigest()


def get_file_metadata(file_path, algorithm):
    try:
        st = os.stat(file_path, follow_symlinks=False)
    except FileNotFoundError:
        return None

    return {
        "hash": calculate_hash(file_path, algorithm),
        "size": st.st_size,
        "mtime": st.st_mtime,
        "ctime": st.st_ctime,
        "mode": st.st_mode,
        "uid": getattr(st, "st_uid", None),
        "gid": getattr(st, "st_gid", None),
    }


def check_single_file(file_path, algorithm):
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        return

    if should_ignore(file_path):
        print(f"Skipped (ignored by pattern): {file_path}")
        return

    file_hash = calculate_hash(file_path, algorithm)
    print(f"\nFile: {file_path}")
    print(f"{algorithm.upper()} Hash: {file_hash}\n")


def check_directory(directory_path, algorithm):
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return

    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if not should_ignore(d)]

        for file_name in files:
            if should_ignore(file_name):
                continue

            file_path = os.path.join(root, file_name)
            calculated_hash = calculate_hash(file_path, algorithm)

            print(f"File: {file_path}")
            print(f"{algorithm.upper()} Hash: {calculated_hash}\n")

def build_baseline(root_dir, algorithm):
    root_dir = os.path.abspath(root_dir)
    baseline = {
        "version": 1,
        "algorithm": algorithm,
        "root": root_dir,
        "created": time.time(),
        "files": {}
    }

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        for file_name in files:
            if should_ignore(file_name):
                continue
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, root_dir)
            meta = get_file_metadata(full_path, algorithm)
            if meta is None:
                continue
            baseline["files"][rel_path] = meta

    return baseline


def save_baseline(baseline, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    print(f"[+] Baseline saved to {out_path}")


def load_baseline(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_baseline(baseline, current_root, algorithm=None):
    current_root = os.path.abspath(current_root)
    algo = algorithm or baseline.get("algorithm", "sha256")

    current_files = {}
    for root, dirs, files in os.walk(current_root):
        dirs[:] = [d for d in dirs if not should_ignore(d)]
        for file_name in files:
            if should_ignore(file_name):
                continue
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, current_root)
            meta = get_file_metadata(full_path, algo)
            if meta is None:
                continue
            current_files[rel_path] = meta

    results = []

    baseline_files = baseline.get("files", {})

    for rel_path, old_meta in baseline_files.items():
        if rel_path not in current_files:
            results.append({
                "path": rel_path,
                "status": "deleted",
                "old": old_meta,
                "new": None,
            })
            continue

        new_meta = current_files[rel_path]
        status = "unchanged"
        if old_meta.get("hash") != new_meta.get("hash"):
            status = "modified"
        else:
            meta_changed = False
            if old_meta.get("mtime") != new_meta.get("mtime") or old_meta.get("ctime") != new_meta.get("ctime"):
                meta_changed = True
            if old_meta.get("mode") != new_meta.get("mode") or old_meta.get("uid") != new_meta.get("uid") or old_meta.get("gid") != new_meta.get("gid"):
                meta_changed = True
            if meta_changed:
                status = "meta_changed"

        results.append({
            "path": rel_path,
            "status": status,
            "old": old_meta,
            "new": new_meta,
        })

    for rel_path, new_meta in current_files.items():
        if rel_path not in baseline_files:
            results.append({
                "path": rel_path,
                "status": "new",
                "old": None,
                "new": new_meta,
            })

    return results


def summarize_results(results):
    counts = {
        "unchanged": 0,
        "modified": 0,
        "deleted": 0,
        "new": 0,
        "meta_changed": 0,
    }
    for r in results:
        s = r["status"]
        if s in counts:
            counts[s] += 1
        else:
            counts[s] = counts.get(s, 0) + 1

    print("\n========== Summary ==========")
    for k in ["unchanged", "modified", "deleted", "new", "meta_changed"]:
        if k in counts:
            print(f"{k}: {counts[k]}")
    for k, v in counts.items():
        if k not in ["unchanged", "modified", "deleted", "new", "meta_changed"]:
            print(f"{k}: {v}")
    print("=============================\n")


def print_detailed_results(results):
    for r in results:
        path = r["path"]
        status = r["status"]
        print(f"[{status}] {path}")


def write_results_json(results, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Comparison results written to JSON: {path}")


def write_results_csv(results, path):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "path", "status",
            "old_hash", "new_hash",
            "old_mtime", "new_mtime",
            "old_ctime", "new_ctime",
            "old_mode", "new_mode",
            "old_uid", "new_uid",
            "old_gid", "new_gid",
        ])
        for r in results:
            old = r.get("old") or {}
            new = r.get("new") or {}
            writer.writerow([
                r["path"],
                r["status"],
                old.get("hash"),
                new.get("hash"),
                old.get("mtime"),
                new.get("mtime"),
                old.get("ctime"),
                new.get("ctime"),
                old.get("mode"),
                new.get("mode"),
                old.get("uid"),
                new.get("uid"),
                old.get("gid"),
                new.get("gid"),
            ])
    print(f"[+] Comparison results written to CSV: {path}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="File Integrity Checker / Baseline Builder (Hybrid: Menu + CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    mode = parser.add_argument_group("Baseline / Compare")
    mode.add_argument("--baseline", help="Create a baseline from this directory")
    mode.add_argument("--compare", help="Compare current directory state to an existing baseline JSON file")
    mode.add_argument("--dir", help="Directory to scan when comparing (defaults to baseline root)")

    algo = parser.add_argument_group("Hashing")
    algo.add_argument("--algo", choices=["md5", "sha1", "sha256", "sha512"], default="sha256",
                      help="Hashing algorithm to use for baseline/compare")

    out = parser.add_argument_group("Output")
    out.add_argument("--out", help="Baseline JSON output path when using --baseline")
    out.add_argument("--json-out", help="Write comparison results to JSON file")
    out.add_argument("--csv-out", help="Write comparison results to CSV file")
    out.add_argument("--summary", action="store_true", help="Show only summary for comparison")
    out.add_argument("--quiet", action="store_true", help="Suppress detailed per-file output")

    return parser.parse_args()

def run_cli_mode():
    args = parse_args()

    if args.baseline:
        root = args.baseline
        algorithm = args.algo
        baseline = build_baseline(root, algorithm)
        out_path = args.out or "baseline.json"
        save_baseline(baseline, out_path)
        return

    if args.compare:
        baseline_path = args.compare
        baseline = load_baseline(baseline_path)
        root = args.dir or baseline.get("root", ".")
        algorithm = baseline.get("algorithm", args.algo)
        results = compare_baseline(baseline, root, algorithm)

        if not args.summary and not args.quiet:
            print_detailed_results(results)

        summarize_results(results)

        if args.json_out:
            write_results_json(results, args.json_out)
        if args.csv_out:
            write_results_csv(results, args.csv_out)
        return

    parse_args().print_help()

def run_menu_mode():
    print(r""" 
    ................................................:::-:.................... . --:.....................
    ..........:::::...........::::::::::--======.##########.======---------==.. ===:-:..................
    ====-:-----=============================##########.##=.. ================.. ===-----:::::...........
    ======================================############..#=    ===============.. ==.=====================
    ====================================############....#.    ===============.. ==.=====================
    =================================##############  #.        ==============.. ========================
    ==============================.  ############=   #.         =============#. ========================
    ================================.     ###.#.#.  #.           ============.. ========================
    =================================       .#..#  ..             ===========.. ========================
    =================================         ..                  ==========-##.========================
    =================================@          .                  =========.#  ========================
    ==================================.         .                    =======..   =======================
    ===================================#         .      #.            ======@.   =======================
    ======-============================@         #    #.   ##.         ======.  ========================
    ==..##..#######............=========#         .  .  #####....       -=.==    =.=====================
    ==..######@###########################        . ##### ##....         =  =   ##==#..######........===
    ==..###=@=@###########################       ####.##.   .               .   #@.##################===
    ==..###===#############################     #=#######=  .:                  =. .#############===@===
    ==..###=################################    ######     .                    = =####..#######====*@==
    ==..###.################################    .    = ==  =-                      .############=====@==
    *=..###=#@##############################            =  =                       =-###########========
    @=..###=##.#############################     #.# ..   .=                        ############====@===
    @=..###=###############################*    ### #.                             .############====@===
    @=..###=##.############################.    ### #. .                            #################===
    @=..###=##=############################=   @.# #.  .                             ################===
    @=..###=##################################### ##=                                ##############=#===
    @=..###=###############.=########@######  #.###..                               .###########@====@@@
    @=..###=############..## .## ######      ####                                    ###########%====..:
    ....###=##@@#######.......  #####   #   ##= #= =                                 .##########-.### ..
    ....##############..     . :#=#..       #. =                                       ...--:...........
    .. .############. ..      # .####-       =.-  =                                    ##.....:.........
    ..........###.  ....      .###.### #- ##  =                                      = #####.#=.........
    .............. .#......   . ####### #####.                                         .#....... ... ...
    ............############   #. .#.   .==                                           .. .....##........
    ...#########.##########:  #   ...  .                                               .#.+..-#..#......
    ####################..  .#.     .  .                                              ...:.#............


                ████████╗██╗  ██╗███████╗      ██████╗  ██████╗ ██╗  ██╗██████╗ ███████╗██████╗ 
                ╚══██╔══╝██║  ██║██╔════╝      ██╔══██╗ ╚════██╗██║  ██║██╔══██╗██╔════╝██╔══██╗
                   ██║   ███████║█████╗ █████╗ ██████╔╝  █████╔╝███████║██████╔╝█████╗  ██████╔╝
                   ██║   ██╔══██║██╔══╝ ╚════╝ ██╔══██╗  ╚═══██╗╚════██║██╔═══╝ ██╔══╝  ██╔═██╗
                   ██║   ██║  ██║███████╗      ██║   ██║██████╔╝     ██║██║     ███████╗██║  ██║
                   ╚═╝   ╚═╝  ╚═╝╚══════╝      ╚═╝   ╚═╝╚═════╝      ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝

                                            File Integrity Checker
                                            Created by: The-R34per

                                    GitHub: https://github.com/The-R34per
                        Website: https://the-r34per.github.io/The-R34per-Website/index.html   
    -----------------------------------------------------------------------------------------------------""")

    time.sleep(2)
    print("\n\n\n")
    print("Choose an option:")
    print("1. Check a single file")
    print("2. Check an entire directory")
    choice = input("Enter 1 or 2: ")

    print("\nChoose a hashing algorithm:")
    print("1. MD5")
    print("2. SHA1")
    print("3. SHA256")
    print("4. SHA512")

    algo_choice = input("Enter 1-4: ")

    algorithms = {
        "1": "md5",
        "2": "sha1",
        "3": "sha256",
        "4": "sha512"
    }

    algorithm = algorithms.get(algo_choice, "sha256")

    if choice == "1":
        file_to_check = input("Enter the file path: ")
        check_single_file(file_to_check, algorithm)
    elif choice == "2":
        directory_to_check = input("Enter the directory to check: ")
        check_directory(directory_to_check, algorithm)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli_mode()
    else:
        run_menu_mode()
