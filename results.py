import os
import re
from collections import defaultdict

RESULTS_DIR = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/real graphs/results quatrilateral"
OUTPUT_DIR  = "summariesReaQuatri"

FNAME_RE       = re.compile(r"^(.+?)_(er|tree|scale_free|real)_results\.txt$")
TIME_RE        = re.compile(r"Done in ([0-9.]+)s")
TIMEOUT_RE     = re.compile(r"TIMED OUT after [0-9.]+s\s+\(elapsed=([0-9.]+)s\)")
TOTAL_ALLOC_RE = re.compile(r"total heap usage: [0-9,]+ allocs, [0-9,]+ frees, ([0-9,]+) bytes allocated")
GRAPH_RE       = re.compile(r"\[Run\] .+ graph=([^\s]+)")

def parse_real_log(path):
    data = {}
    cur_graph = None
    with open(path) as f:
        for line in f:
            m = GRAPH_RE.search(line)
            if m:
                cur_graph = m.group(1)
                data[cur_graph] = {"time": None, "mem": None, "timeout": False}
                continue
            if cur_graph is None:
                continue
            m = TIMEOUT_RE.search(line)
            if m:
                data[cur_graph]["timeout"] = True
                data[cur_graph]["time"] = None
                continue
            m = TIME_RE.search(line)
            if m:
                data[cur_graph]["timeout"] = False
                data[cur_graph]["time"] = float(m.group(1))
                continue
            m = TOTAL_ALLOC_RE.search(line)
            if m:
                data[cur_graph]["mem"] = int(m.group(1).replace(",", ""))
                continue
    return data

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fn in os.listdir(RESULTS_DIR):
        m = FNAME_RE.match(fn)
        if not m:
            continue
        solver, family = m.group(1), m.group(2)
        if family != "real":
            continue
        parsed = parse_real_log(os.path.join(RESULTS_DIR, fn))
        out_path = os.path.join(OUTPUT_DIR, f"{solver}_real_summary.txt")
        with open(out_path, "w") as out:
            out.write(f"=== Summary for solver: {solver} (real graphs) ===\n\n")
            hdr = ["graph", "time(s)", "alloc(B)"]
            out.write(" | ".join(hdr) + "\n")
            for graph in sorted(parsed.keys()):
                rec = parsed[graph]
                t = "NaN" if rec["timeout"] or rec["time"] is None else f"{rec['time']:.3f}"
                m = str(rec["mem"]) if rec["mem"] is not None else "NaN"
                out.write(f"{graph} | {t} | {m}\n")
        print(f"Wrote summary for {solver} → {out_path}")

if __name__ == "__main__":
    main()