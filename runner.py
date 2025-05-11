import os
import shutil
import subprocess
import time


# Step 1: Configuration

TEST_SOURCE_DIRS = {
    "lad": {
        "er": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/er_lad",
        "tree": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/tree_lad",
        "scale_free": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/scalefree_lad",
    },
    #"ri": {
    #    "er": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/er_ri",
    #    "tree": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/tree_ri",
    #    "scale_free": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/scalefree_ri",
    #},
    #"vf3": {
    #    "er": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/er_vf3",
    #    "tree": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/tree_vf3",
    #    "scale_free": "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/scalefree_vf3",
    #}
}

SOLVER_DEST_DIRS = {
    #"Glasgow": "/home/jana/Documents/DIPLOMA/SOLVERJI/GLASGOW/glasgow-subgraph-solver/test",
    #"LAD":     "/home/jana/Documents/DIPLOMA/SOLVERJI/LAD/pathLAD/test",
    #"RI":      "/home/jana/Documents/DIPLOMA/SOLVERJI/RI/RI/test",
    #"VF3":     "/home/jana/Documents/DIPLOMA/SOLVERJI/VF3/vf3lib/test",
    "SICS":    "/home/jana/Documents/DIPLOMA/SOLVERJI/SICS/sics/test",
}

SOLVER_FORMAT = {
    #"Glasgow": "lad",
    #"LAD": "lad",
    "SICS": "lad",
    #"RI": "ri",
    #"VF3": "vf3",
}

# Step 2: Helper for logging

def log_print(msg, log_file):
    log_file.write(msg + "\n")
    log_file.flush()


# Step 3: Copy & clean test files

def copy_tests(solver_name, test_type):
    fmt = SOLVER_FORMAT.get(solver_name)
    src = TEST_SOURCE_DIRS.get(fmt, {}).get(test_type)
    dst_base = SOLVER_DEST_DIRS.get(solver_name)
    if not src or not dst_base or not os.path.isdir(src):
        print(f"[Copy] Skipping {solver_name}/{test_type} (src or dst missing)")
        return

    dst = os.path.join(dst_base, test_type)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    print(f"[Copy] {solver_name}: copying {test_type} → {dst}")
    for f in os.listdir(src):
        sp = os.path.join(src, f)
        dp = os.path.join(dst, f)
        if os.path.isfile(sp):
            shutil.copy2(sp, dp)


# Step 4: Run tests for one solver & one type


def run_all_tests_for_solver(solver, test_type, log_file):
    test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], test_type)

    # determine filename suffix
    if solver["name"] in ("Glasgow", "LAD", "SICS"):
        suffix = "_original_graph"
    elif solver["name"] == "RI":
        suffix = "_original_graph.gfu"
    else:
        suffix = "graph.grf"

    # collect and sort group IDs
    groups = [f[:-len(suffix)] for f in os.listdir(test_dir) if f.endswith(suffix)]
    try:
        groups.sort(key=int)
    except ValueError:
        groups.sort()

    log_print(f"[Run] {solver['name']} ({test_type}) groups: {groups}", log_file)

    for grp in groups:
        # absolute target path
        target_file = solver["file_pattern"]["target"].format(group=grp)
        target_abs  = os.path.join(test_dir, target_file)
        if not os.path.exists(target_abs):
            log_print(f"[Run] Missing target {target_abs}", log_file)
            continue

        for lvl in (10, 20, 60):
            # absolute pattern path
            pattern_file = solver["file_pattern"]["pattern"].format(group=grp, level=lvl)
            pattern_abs  = os.path.join(test_dir, pattern_file)
            if not os.path.exists(pattern_abs):
                log_print(f"[Run] Missing pattern {pattern_abs}", log_file)
                continue

            # relative paths for execution
            pattern_rel = "./" + os.path.relpath(pattern_abs, solver["workdir"])
            target_rel  = "./" + os.path.relpath(target_abs,  solver["workdir"])

            # build the base solver command
            base_cmd = solver["command"].format(pattern=pattern_rel, target=target_rel)

            # wrap in Valgrind Memcheck
            vg_log = f"valgrind_{solver['name']}_{test_type}_grp{grp}_lvl{lvl}.log"
            vg_cmd = (
                f"valgrind "
                f"--tool=memcheck "
                f"--leak-check=full "
                f"--track-origins=yes "
                f"--log-file={vg_log} "
                f"{base_cmd}"
            )

            log_print(f"\n[Run] {solver['name']} grp={grp} lvl={lvl}", log_file)
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
                    timeout=60.0
                )
                elapsed = time.time() - start
                log_print(f"[Run] Done in {elapsed:.2f}s", log_file)

            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                log_print(f"[Run] TIMED OUT after 60s (elapsed={elapsed:.2f}s)", log_file)
                continue

            # log solver output
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



# Step 5: Main – iterate all three graph families

def main():
    all_types = ["er", "tree", "scale_free"]

    # Copy & clean
    for t in all_types:
        for solver_name in SOLVER_DEST_DIRS:
            copy_tests(solver_name, t)

    # ensure results dir
    os.makedirs("results", exist_ok=True)

    solvers = [
        {
            "name": "SICS",
            "workdir": "/home/jana/Documents/DIPLOMA/SOLVERJI/SICS/sics",
            "command": "./a.out {pattern} {target}",
            "file_pattern": {
                "target": "{group}_original_graph",
                "pattern": "{group}_subgraph_{level}"
            }
        }
    ]

    # Run & log
    for t in all_types:
        for solver in solvers:
            test_dir = os.path.join(SOLVER_DEST_DIRS[solver["name"]], t)
            if not os.path.isdir(test_dir):
                print(f"[Skip] {solver['name']} has no '{t}' tests, skipping.")
                continue
            log_path = os.path.join("results", f"{solver['name']}_{t}_results.txt")
            with open(log_path, "w") as lf:
                log_print(f"=== START {solver['name']} ({t}) ===", lf)
                run_all_tests_for_solver(solver, t, lf)
                log_print(f"=== END   {solver['name']} ({t}) ===", lf)
            print(f"[Done] {solver['name']} {t} → {log_path}")

if __name__ == "__main__":
    main()
