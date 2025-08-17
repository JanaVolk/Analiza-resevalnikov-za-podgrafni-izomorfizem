import pandas as pd
import matplotlib.pyplot as plt
import glob, os

# 1) Collect counts of non-NaN times from all *_summary.csv
counts = {}
families = set()

for path in glob.glob('*_summary.txt'):
    fname = os.path.basename(path)
    solver, *fam_parts, _ = fname.split('_')
    family = '_'.join(fam_parts).replace('_summary', '')
    
    # Read, splitting on "|" or whitespace — adjust sep if needed
    df = pd.read_csv(path, sep=r'\s*\|\s*', engine='python', na_values=['NaN'])
    
    # Find the time column automatically
    time_col = [c for c in df.columns if 'time' in c.lower()][0]
    solved = df[time_col].notna().sum()
    
    counts.setdefault(solver, {})[family] = solved
    families.add(family)

# 2) Build a solver × family DataFrame
df = pd.DataFrame(counts).T.fillna(0).astype(int)
df = df.reindex(sorted(df.index))            # sort solvers alphabetically
df = df[sorted(families)]                     # sort families

# 3) Plot stacked bar chart
ax = df.plot(
    kind='bar',
    stacked=True,
    edgecolor='black',
    figsize=(8,5)
)
ax.set_xlabel('Solver')
ax.set_ylabel('Number of Solved Instances')
ax.set_title('Solver Performance Across Test Families')
ax.legend(title='Test Family', bbox_to_anchor=(1.02,1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
