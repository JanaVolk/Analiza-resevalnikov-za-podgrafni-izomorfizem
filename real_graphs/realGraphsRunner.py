import os
import shutil
import subprocess
import time

REAL_GRAPHS_DIR = "/home/jana/Documents/DIPLOMA/REAL TESTI/REAL"
SUBGRAPH_DIR = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/real graphs/generating instances/pentagon"

SOLVER_DEST_DIRS = {
    "Glasgow": "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/testReal",
    "LAD":     "/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD/testReal",
    "RI":      "/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI/testReal",
    "VF3":     "/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib/testReal",
    "SICS":    "/home/jana/Documents/DIPLOMA/SOLVERJI/SICS/sics/testReal",
}

SUBGRAPH_FILE = {
    "Glasgow": "pentagonLAD",
    "LAD":     "pentagonLAD",
    "SICS":    "pentagonLAD",
    "RI":      "pentagonRI.gfu",
    "VF3":     "pentagonVF3.sub.grf",
}

def log_print(msg, log_file):
    log_file.write(msg + "\n")
    log_file.flush()

def copy_real_tests(solver_name):
    dst_base = SOLVER_DEST_DIRS.get(solver_name)
    subgraph_file = SUBGRAPH_FILE.get(solver_name)
    if not dst_base or not subgraph_file:
        print(f"[Copy] Skipping {solver_name} (dst or subgraph file missing)")
        return

    if solver_name in ["Glasgow", "LAD", "SICS"]:
        real_graphs_src = os.path.join(REAL_GRAPHS_DIR, "LAD")
    elif solver_name == "RI":
        real_graphs_src = os.path.join(REAL_GRAPHS_DIR, "RI")
    elif solver_name == "VF3":
        real_graphs_src = os.path.join(REAL_GRAPHS_DIR, "VF3")
    else:
        print(f"[Copy] Unknown solver: {solver_name}")
        return

    dst = os.path.join(dst_base, "real")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    # Copy real graphs
    for f in os.listdir(real_graphs_src):
        sp = os.path.join(real_graphs_src, f)
        dp = os.path.join(dst, f)
        if os.path.isfile(sp):
            shutil.copy2(sp, dp)

    # Copy subgraph file
    subgraph_src = os.path.join(SUBGRAPH_DIR, subgraph_file)
    subgraph_dst = os.path.join(dst, subgraph_file)
    if os.path.isfile(subgraph_src):
        shutil.copy2(subgraph_src, subgraph_dst)
    else:
        print(f"[Copy] subgraph file {subgraph_src} not found for {solver_name}")

    print(f"[Copy] {solver_name}: copied real graphs and subgraph file to {dst}")

def run_real_tests_for_solver(solver, log_file):
    test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], "real")
    subgraph_file = SUBGRAPH_FILE[solver["name"]]

    real_graphs = [f for f in os.listdir(test_dir)
                   if f != subgraph_file and os.path.isfile(os.path.join(test_dir, f))]
    real_graphs.sort()

    # subgraph path
    pattern_abs = os.path.join(test_dir, subgraph_file)
    if not os.path.isfile(pattern_abs):
        log_print(f"[Run] No subgraph subgraph '{subgraph_file}' found!", log_file)
        return

    for real_graph in real_graphs:
        target_abs = os.path.join(test_dir, real_graph)

        # relative paths for execution
        pattern_rel = "./" + os.path.relpath(pattern_abs, solver["workdir"])
        target_rel  = "./" + os.path.relpath(target_abs,  solver["workdir"])

        base_cmd = solver["command"].format(pattern=pattern_rel, target=target_rel)

        vg_log = f"valgrind_{solver['name']}_real_{real_graph}.log"
        vg_cmd = (
            f"valgrind "
            f"--tool=memcheck "
            f"--leak-check=full "
            f"--track-origins=yes "
            f"--log-file={vg_log} "
            f"{base_cmd}"
        )

        log_print(f"\n[Run] {solver['name']} real graph={real_graph}", log_file)
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
    # copy, clean
    for solver_name in SOLVER_DEST_DIRS:
        copy_real_tests(solver_name)

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
        test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], "real")
        if not os.path.isdir(test_dir):
            print(f"[Skip] {solver['name']} has no 'real' tests, skipping.")
            continue
        log_path = os.path.join("results", f"{solver['name']}_real_results.txt")
        with open(log_path, "w") as lf:
            log_print(f"=== START {solver['name']} (real) ===", lf)
            run_real_tests_for_solver(solver, lf)
            log_print(f"=== END   {solver['name']} (real) ===", lf)
        print(f"[Done] {solver['name']} real → {log_path}")

if __name__ == "__main__":
    main()