import os
import re
from collections import defaultdict

RESULTS_DIR = "AAA"
OUTPUT_DIR  = "summaries5"

# parse filenames "LAD_er_results.txt"
FNAME_RE       = re.compile(r"^(.+?)_(er|tree|scale_free)_results\.txt$")
GRP_LVL_RE     = re.compile(r"grp=(\d+)\s+lvl=(10|20|60)")
TIME_RE        = re.compile(r"Done in ([0-9.]+)s")
TIMEOUT_RE     = re.compile(r"TIMED OUT after [0-9.]+s\s+\(elapsed=([0-9.]+)s\)")

TOTAL_ALLOC_RE = re.compile(
    r"total heap usage: [0-9,]+ allocs, [0-9,]+ frees, ([0-9,]+) bytes allocated"
)

# solver-specific patterns
LAD_ELAPSED_RE      = re.compile(r"Run completed:.*elapsed=([0-9.]+)s")
GLASGOW_RUNTIME_RE = re.compile(r"runtime\s*=\s*([0-9.]+)")
RI_TOTAL_RE        = re.compile(r"total time:\s*([0-9.]+)")
SICS_FIRST_MS_RE   = re.compile(r"Time to find first induced isomorphism:\s*([0-9.]+)\s*ms")
VF3_PAIRTIME_RE    = re.compile(r"^\s*\d+\s+([0-9.]+)\s+[0-9.]+")

def parse_log(path):
    """
    Returns dict[(group:int, level:int)] = {
        "time":  float,  # solver run time (seconds)
        "mem":   int,    # total bytes allocated over the run
        "timeout": bool  # True if TIMED OUT
    }
    """
    data = {}
    solver = os.path.basename(path).split('_', 1)[0]
    cur_grp = cur_lvl = None

    with open(path) as f:
        for line in f:
            # group & level context
            m = GRP_LVL_RE.search(line)
            if m:
                cur_grp, cur_lvl = int(m.group(1)), int(m.group(2))
                continue

            # timeout
            m = TIMEOUT_RE.search(line)
            if m:
                rec = data.setdefault((cur_grp, cur_lvl), {})
                rec["timeout"] = True
                rec["time"]    = float(m.group(1))
                continue

            # solver-specific timing
            if solver == "LAD":
                m = LAD_ELAPSED_RE.search(line)
                if m:
                    rec = data.setdefault((cur_grp, cur_lvl), {})
                    rec["timeout"] = False
                    rec["time"]    = float(m.group(1))
                    continue

            if solver == "Glasgow":
                # runtime in ms convert to s 
                m = GLASGOW_RUNTIME_RE.search(line)
                if m:
                    rec = data.setdefault((cur_grp, cur_lvl), {})
                    rec["timeout"] = False
                    rec["time"]    = float(m.group(1)) / 1000.0
                    continue

            if solver == "RI":
                m = RI_TOTAL_RE.search(line)
                if m:
                    rec = data.setdefault((cur_grp, cur_lvl), {})
                    rec["timeout"] = False
                    rec["time"]    = float(m.group(1))
                    continue

            if solver == "SICS":
                m = SICS_FIRST_MS_RE.search(line)
                if m:
                    rec = data.setdefault((cur_grp, cur_lvl), {})
                    rec["timeout"] = False
                    rec["time"]    = float(m.group(1)) / 1000.0
                    continue

            if solver == "VF3":
                m = VF3_PAIRTIME_RE.search(line)
                if m:
                    rec = data.setdefault((cur_grp, cur_lvl), {})
                    rec["timeout"] = False
                    rec["time"]    = float(m.group(1))
                    continue

            m = TIME_RE.search(line)
            if m:
                rec = data.setdefault((cur_grp, cur_lvl), {})
                rec["timeout"] = False
                rec["time"]    = float(m.group(1))
                continue

            m = TOTAL_ALLOC_RE.search(line)
            if m:
                rec = data.setdefault((cur_grp, cur_lvl), {})
                rec["mem"]    = int(m.group(1).replace(",", ""))
                continue

    return data

def main():
    data = defaultdict(dict)
    levels = [10, 20, 60]

    # read logs
    for fn in os.listdir(RESULTS_DIR):
        m = FNAME_RE.match(fn)
        if not m:
            continue
        solver, family = m.group(1), m.group(2)
        data[solver][family] = parse_log(os.path.join(RESULTS_DIR, fn))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # write summaries
    for solver, famdict in data.items():
        out_path = os.path.join(OUTPUT_DIR, f"{solver}_summary.txt")
        with open(out_path, "w") as out:
            out.write(f"=== Summary for solver: {solver} ===\n\n")
            for family in ("er", "tree", "scale_free"):
                parsed = famdict.get(family, {})
                if not parsed:
                    continue

                out.write(f"-- test family: {family} --\n")
                hdr = ["group"] + \
                      [f"{lvl}_time(s)"  for lvl in levels] + \
                      [f"{lvl}_alloc(B)" for lvl in levels]
                out.write(" | ".join(hdr) + "\n")

                groups = sorted({grp for (grp, lvl) in parsed.keys()})
                for grp in groups:
                    row = [str(grp)]
                    # times
                    for lvl in levels:
                        rec = parsed.get((grp, lvl), {})
                        if rec.get("timeout"):
                            row.append("TIMEOUT")
                        elif "time" in rec:
                            row.append(f"{rec['time']:.3f}")
                        else:
                            row.append("")
                    # total bytes allocated
                    for lvl in levels:
                        rec = parsed.get((grp, lvl), {})
                        row.append(str(rec.get("mem", "")))
                    out.write(" | ".join(row) + "\n")
                out.write("\n")

        print(f"Wrote summary for {solver} → {out_path}")

if __name__ == "__main__":
    main()
