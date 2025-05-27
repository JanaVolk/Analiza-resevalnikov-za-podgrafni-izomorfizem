import os
import shutil
import subprocess
import time


RANDOM_GRAPHS_DIR = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/random_graphs/instances"

SOLVER_DEST_DIRS = {
    "Glasgow": "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/testRandom",
    "LAD":     "/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD/testRandom",
    "RI":      "/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI/testRandom",
    "VF3":     "/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib/testRandom",
    "SICS":    "/home/jana/Documents/DIPLOMA/SOLVERJI/SICS/sics/testRandom",
}

SUBGRAPH_FILE = {
    "Glasgow": "subgraph50.lad",
    "LAD":     "subgraph50.lad",
    "SICS":    "subgraph50.lad",
    "RI":      "subgraph50.gfu",
    "VF3":     "subgraph50.sub.grf",
}

def log_print(msg, log_file):
    log_file.write(msg + "\n")
    log_file.flush()

def copy_random_tests(solver_name):
    dst_base = SOLVER_DEST_DIRS.get(solver_name)
    subgraph_file = SUBGRAPH_FILE.get(solver_name)
    solver_to_subfolder = {
        "Glasgow": "LAD",
        "LAD": "LAD",
        "SICS": "LAD",
        "RI": "RI",
        "VF3": "VF3",
    }
    subfolder = solver_to_subfolder.get(solver_name)
    if not dst_base or not subgraph_file or not subfolder:
        print(f"[Copy] Skipping {solver_name} (dst or subgraph file missing)")
        return

    src_dir = os.path.join(RANDOM_GRAPHS_DIR, subfolder)
    dst = os.path.join(dst_base, "random")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    for f in os.listdir(src_dir):
        sp = os.path.join(src_dir, f)
        dp = os.path.join(dst, f)
        if os.path.isfile(sp):
            shutil.copy2(sp, dp)

    subgraph_src = os.path.join(src_dir, subgraph_file)
    subgraph_dst = os.path.join(dst, subgraph_file)
    if os.path.isfile(subgraph_src):
        shutil.copy2(subgraph_src, subgraph_dst)
    else:
        print(f"[Copy] subgraph file {subgraph_src} not found for {solver_name}")

    print(f"[Copy] {solver_name}: copied random graphs and subgraph file to {dst}")

def run_random_tests_for_solver(solver, log_file):
    test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], "random")
    subgraph_file = SUBGRAPH_FILE[solver["name"]]

    random_graphs = [f for f in os.listdir(test_dir)
                     if f != subgraph_file and os.path.isfile(os.path.join(test_dir, f))]
    random_graphs.sort()

    pattern_abs = os.path.join(test_dir, subgraph_file)
    if not os.path.isfile(pattern_abs):
        log_print(f"[Run] No subgraph '{subgraph_file}' found!", log_file)
        return

    for random_graph in random_graphs:
        target_abs = os.path.join(test_dir, random_graph)

        pattern_rel = "./" + os.path.relpath(pattern_abs, solver["workdir"])
        target_rel  = "./" + os.path.relpath(target_abs,  solver["workdir"])

        base_cmd = solver["command"].format(pattern=pattern_rel, target=target_rel)

        vg_log = f"valgrind_{solver['name']}_random_{random_graph}.log"
        vg_cmd = (
            f"valgrind "
            f"--tool=memcheck "
            f"--leak-check=full "
            f"--track-origins=yes "
            f"--log-file={vg_log} "
            f"{base_cmd}"
        )

        log_print(f"\n[Run] {solver['name']} random graph={random_graph}", log_file)
        log_print(f"[Run] CMD: {vg_cmd}", log_file)

        start = time.time()
        try:
            proc = subprocess.run(
                vg_cmd,
                cwd=solver["workdir"],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=120.0
            )
            elapsed = time.time() - start
            log_print(f"[Run] Done in {elapsed:.2f}s", log_file)

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            log_print(f"[Run] TIMED OUT after 120s (elapsed={elapsed:.2f}s)", log_file)
            continue

        if proc.stdout:
            log_print(proc.stdout, log_file)
        if proc.stderr:
            log_print(proc.stderr, log_file)

        # Valgrind log for HEAP SUMMARY
        vg_path = os.path.join(solver["workdir"], vg_log)
        heap_in_use = None
        total_usage = None
        if os.path.exists(vg_path):
            with open(vg_path) as vg_f:
                for line in vg_f:
                    if "in use at exit:" in line:
                        heap_in_use = line.strip()
                    elif "total heap usage:" in line:
                        total_usage = line.strip()
                    if heap_in_use and total_usage:
                        break

        if heap_in_use:
            log_print(f"[Valgrind] {heap_in_use}", log_file)
        if total_usage:
            log_print(f"[Valgrind] {total_usage}", log_file)

def main():
    for solver_name in SOLVER_DEST_DIRS:
        copy_random_tests(solver_name)

    os.makedirs("results", exist_ok=True)

    solvers = [
        {
            "name": "Glasgow",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver",
            "command": "./build/glasgow_subgraph_solver --timeout 120 --induced --format lad {pattern} {target}",
        },
        {
            "name": "LAD",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD",
            "command": "./main -s 120 -f -i -p {pattern} -t {target}",
        },
        {
            "name": "RI",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI",
            "command": "./ri36 ind gfu {target} {pattern}",
        },
        {
            "name": "VF3",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib",
            "command": "./bin/vf3 -u {pattern} {target}",
        },
        {
            "name": "SICS",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/SICS/sics",
            "command": "./a.out {pattern} {target}",
        }
    ]

    for solver in solvers:
        test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], "random")
        if not os.path.isdir(test_dir):
            print(f"[Skip] {solver['name']} has no 'random' tests, skipping.")
            continue
        log_path = os.path.join("results", f"{solver['name']}_random_results.txt")
        with open(log_path, "w") as lf:
            log_print(f"=== START {solver['name']} (random) ===", lf)
            run_random_tests_for_solver(solver, lf)
            log_print(f"=== END   {solver['name']} (random) ===", lf)
        print(f"[Done] {solver['name']} random → {log_path}")

if __name__ == "__main__":
    main()