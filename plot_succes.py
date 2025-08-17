import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os, io, glob
import re

summary_dirs = {
   "generated_graphs": "generated_graphs/summaries",
   "random_graphs":    "random_graphs/summaries",
   "real_graphs":      "real_graphs/summaries",
}

solvers = ["Glasgow", "PathLAD", "RI", "SICS", "VF3"]

group_colors = {
   # ER - pink
   "ER-10":        "#FFC2D1",
   "ER-20":        "#FF7497",
   "ER-60":        "#FC2259",

   # Tree - purple
   "MST-10":       "#A628CC",
   "MST-20":       "#8316E9",
   "MST-60":       "#60079C",

   # Scale-free - blue
   "SF-10":        "#A1C9F7",
   "SF-20":        "#8698E9",
   "SF-60":        "#5A3ECC",

   # Random graphs - red
   "IBU-500-50":   "#F3722C",
   "IBU-700-70":   "#C93C1A",
   "IBU-1000-100": "#9E0507",

   # Real graphs - green
   "R3C":          "#C5C35E",
   "R4C":          "#7EB356",
   "R5C":          "#618D3F",

   # fallback
   "other":        "#F9C74F",
}

all_groups = [
   # generated-graphs:
   "ER-10", "ER-20", "ER-60",
   "MST-10", "MST-20", "MST-60",
   "SF-10", "SF-20", "SF-60",
   # random-graphs:
   "IBU-500-50", "IBU-700-70", "IBU-1000-100",
   # real-graphs:
   "R3C", "R4C", "R5C"
]

file_to_display_mapping = {
   # Generated graphs mapping
   "er_10": "ER-10",
   "er_20": "ER-20", 
   "er_60": "ER-60",
   "tree_10": "MST-10",
   "tree_20": "MST-20",
   "tree_60": "MST-60",
   "scale_free_10": "SF-10",
   "scale_free_20": "SF-20",
   "scale_free_60": "SF-60",
   
   # Random graphs mapping
   "random_500-50": "IBU-500-50",
   "random_700-70": "IBU-700-70", 
   "random_1000-100": "IBU-1000-100",
   
   # Real graphs mapping
   "triangle": "R3C",
   "quatrilateral": "R4C",
   "pentagon": "R5C"
}

def count_times(df):
   col = next((c for c in df.columns if "time" in c.lower()), None)
   if col is None:
       return 0
   df[col] = pd.to_numeric(df[col], errors="coerce")
   return df[col].notna().sum()

def map_solver_name(solver):
   return "PathLAD" if solver == "LAD" else solver

group_solver = {s: {g: 0 for g in all_groups} for s in solvers}

for kind, folder in summary_dirs.items():
   for path in glob.glob(os.path.join(folder, "*_summary.txt")):
       fname = os.path.basename(path)

       if kind == "generated_graphs":
           base, _ = os.path.splitext(fname)
           solver = map_solver_name(base.replace("_summary", ""))

           lines = open(path).readlines()
           curr, buf = None, []
           for L in lines:
               if L.startswith("-- test family:"):
                   if curr and buf:
                       df = pd.read_csv(io.StringIO("".join(buf)),
                                        sep=r"\s*\|\s*", engine="python")
                       df.columns = df.columns.str.strip()
                       for col in df.columns:
                           m = re.match(r"(\d+)_time", col)
                           if m:
                               pct = m.group(1)
                               grp_file = f"{curr}_{pct}"
                               grp_display = file_to_display_mapping.get(grp_file, grp_file)
                               if grp_display in all_groups:
                                   group_solver[solver][grp_display] += df[col].notna().sum()

                   fam_raw   = L[len("-- test family:"):].strip()
                   fam_clean = fam_raw.strip("- ").strip().replace("-", "_")
                   curr      = fam_clean
                   buf = []

               elif "|" in L:
                   buf.append(L)

           if curr and buf:
               df = pd.read_csv(io.StringIO("".join(buf)),
                                sep=r"\s*\|\s*", engine="python")
               df.columns = df.columns.str.strip()
               for col in df.columns:
                   m = re.match(r"(\d+)_time", col)
                   if m:
                       pct = m.group(1)
                       grp_file = f"{curr}_{pct}"
                       grp_display = file_to_display_mapping.get(grp_file, grp_file)
                       if grp_display in all_groups:
                           group_solver[solver][grp_display] += df[col].notna().sum()

       else:
           base, _ = os.path.splitext(fname)
           parts = base.split("_")
           solver = map_solver_name(parts[0])

           with open(path) as f:
               piped = [l for l in f if "|" in l]
           df = pd.read_csv(io.StringIO("".join(piped)),
                            sep=r"\s*\|\s*", engine="python")
           df.columns = df.columns.str.strip()
           time_col = next(c for c in df.columns if "time" in c.lower())
           df[time_col] = pd.to_numeric(df[time_col], errors="coerce")

           if kind == "random_graphs":
               size_map = {
                   "500":  "IBU-500-50",
                   "700":  "IBU-700-70",
                   "1000": "IBU-1000-100",
               }
               graph_col = df.columns[0]
               for size, grp in size_map.items():
                   mask = df[graph_col].str.contains(f"_graph_{size}")
                   group_solver[solver][grp] += df.loc[mask, time_col].notna().sum()

           else:
               # real_graphs
               raw_group = "_".join(parts[1:-1])
               grp_display = file_to_display_mapping.get(raw_group, raw_group)
               if grp_display in all_groups:
                   group_solver[solver][grp_display] += df[time_col].notna().sum()

df_counts = (
   pd.DataFrame(group_solver)
     .T
     .reindex(solvers)[all_groups]
     .fillna(0)
     .astype(int)
)

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(solvers))
bottom = np.zeros(len(solvers), dtype=int)

for grp in all_groups:
   vals = df_counts[grp].values
   ax.bar(x, vals, bottom=bottom, label=grp, color=group_colors[grp])
   bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(solvers, rotation=45, ha="right")
ax.set_ylabel("število rešenih primerov")
ax.set_xlabel("reševalniki")

max_total = bottom.max()
ax.set_ylim(0, max_total * 1.05)

yt = list(ax.get_yticks())
if max_total not in yt:
   yt.append(max_total)
   yt = sorted(yt)
ax.set_yticks(yt)

handles, labels = ax.get_legend_handles_labels()
seen = set()
h2, l2 = [], []
for h, L in zip(handles, labels):
   if L not in seen:
       seen.add(L)
       h2.append(h)
       l2.append(L)

h2 = h2[::-1]
l2 = l2[::-1]

ax.legend(h2, l2, title="Legenda", bbox_to_anchor=(1.02,1), loc="upper left")

plt.tight_layout()
plt.savefig("solver_success.png", dpi=150)
plt.show()