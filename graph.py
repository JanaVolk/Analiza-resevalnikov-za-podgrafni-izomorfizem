import os
import pandas as pd
import matplotlib.pyplot as plt

folder_path = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/real_graphs/summaries"

def clean_and_sort_data(df, column_to_sort):
    df[column_to_sort] = pd.to_numeric(df[column_to_sort], errors='coerce')
    df = df.sort_values(by=column_to_sort, ascending=True, na_position='last')
    return df

# REAL
def load_real_summary_files(folder_path, graph_type):
    data = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith("_summary.txt") and graph_type in file_name:
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path, sep="|", skiprows=2, names=["graph", "time(s)", "alloc(B)"])
            df["time(s)"] = pd.to_numeric(df["time(s)"].str.strip(), errors='coerce')
            df["alloc(B)"] = pd.to_numeric(df["alloc(B)"].str.strip(), errors='coerce')
            solver_name = file_name.split("_")[0]
            data[solver_name] = df
    return data

def plot_cumulative_real(data, time_limit=120, save_path=None):
    plt.figure(figsize=(10, 6))
    for solver, df in data.items():
        times = df["time(s)"].dropna().sort_values()
        solved = (times <= time_limit).cumsum()
        x = [0] + list(times[times <= time_limit])
        y = [0] + list(range(1, len(x)))
        if len(x) > 0 and x[-1] < time_limit:
            x.append(time_limit)
            y.append(y[-1])
        plt.plot(x, y, label=solver)
    plt.xlim(0, time_limit)
    plt.ylim(0, None)
    plt.xlabel("čas [s]")
    plt.ylabel("število rešenih primerov")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.grid()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def plot_memory_time_real(data, time_limit=120, save_path=None):
    plt.figure(figsize=(10, 6))
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    max_mem = 0
    for idx, (solver, df) in enumerate(data.items()):
        times = pd.to_numeric(df["time(s)"], errors='coerce')
        mems = pd.to_numeric(df["alloc(B)"], errors='coerce') / (1024 * 1024)  # MB
        mask = (~times.isna()) & (~mems.isna()) & (times <= time_limit)
        plt.scatter(times[mask], mems[mask], color=colors[idx % len(colors)], label=solver, s=40)
        if mems[mask].max(skipna=True) > max_mem:
            max_mem = mems[mask].max(skipna=True)
    plt.xlim(0, time_limit)
    plt.ylim(0, max_mem * 1.05 if max_mem > 0 else 1)
    plt.xlabel("čas [s]")
    plt.ylabel("poraba pomnilnika [MB]")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.grid()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

# GENERATED
def load_and_process_summary_files(folder_path, graph_type):
    data = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith("_summary.txt"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as f:
                lines = f.readlines()
            section_start = None
            for idx, line in enumerate(lines):
                if f"-- test family: {graph_type} --" in line:
                    section_start = idx
                    break
            if section_start is not None:
                header_idx = section_start + 1
                data_start = section_start + 2
                content = []
                for line in lines[data_start:]:
                    if not line.strip() or line.startswith("-- test family:"):
                        break
                    content.append(line.strip())
                if content:
                    df = pd.DataFrame([row.split(" | ") for row in content])
                    df.columns = ["group", "10_time(s)", "20_time(s)", "60_time(s)", "10_alloc(B)", "20_alloc(B)", "60_alloc(B)"]
                    solver_name = file_name.split("_")[0]
                    data[solver_name] = df
    return data

real_graph_types = ["pentagon", "quatrilateral", "triangle"]

for graph_type in real_graph_types:
    summary_data = load_real_summary_files(folder_path, graph_type)
    plot_cumulative_real(summary_data, time_limit=120, save_path=f"{graph_type}.png")
    plot_memory_time_real(summary_data, time_limit=120, save_path=f"{graph_type}_memory.png")

def plot_cumulative_graph(data, column_to_sort, graph_type, save_path=None):
    plt.figure(figsize=(10, 6))
    for solver, df in data.items():
        df = clean_and_sort_data(df, column_to_sort)
        total_instances = len(df)
        if total_instances == 0:
            continue
        valid_data = df[column_to_sort].dropna()
        solved_counts = valid_data.rank(method='min', pct=False)
        x = list(valid_data)
        y = list(solved_counts)
        x = [0] + x
        y = [0] + y
        if x[-1] < 60:
            x.append(60)
            y.append(y[-1])
        elif x[-1] > 60:
            x[-1] = 60
        plt.plot(x, y, linestyle='-', label=solver)
    plt.xlim(0, 60)
    plt.ylim(0, 100)
    plt.xlabel("čas [s]")
    plt.ylabel("število rešenih primerov")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.grid()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

graph_types = ["tree", "er", "scale_free"]
time_columns = ["10_time(s)", "20_time(s)", "60_time(s)"]

for graph_type in graph_types:
    summary_data = load_and_process_summary_files(folder_path, graph_type)
    for time_column in time_columns:
        save_name = f"{graph_type}{time_column.split('_')[0]}.png"
        plot_cumulative_graph(summary_data, time_column, graph_type, save_path=save_name)

def plot_memory_time(data, time_column, memory_column, graph_type, save_path=None):
    plt.figure(figsize=(10, 6))
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    max_mem = 0
    for idx, (solver, df) in enumerate(data.items()):
        times = pd.to_numeric(df[time_column], errors='coerce')
        mems = pd.to_numeric(df[memory_column], errors='coerce') / (1024 * 1024)  # Convert to MB
        mask = (~times.isna()) & (~mems.isna()) & (times <= 60)
        plt.scatter(times[mask], mems[mask], color=colors[idx % len(colors)], label=solver, s=40)
        if mems[mask].max(skipna=True) > max_mem:
            max_mem = mems[mask].max(skipna=True)
    plt.xlim(0, 60)
    plt.ylim(0, max_mem * 1.05 if max_mem > 0 else 1)
    plt.xlabel("čas [s]")
    plt.ylabel("poraba pomnilnika [MB]")  # Update label to MB
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.grid()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

memory_columns = ["10_alloc(B)", "20_alloc(B)", "60_alloc(B)"]

for graph_type in graph_types:
    summary_data = load_and_process_summary_files(folder_path, graph_type)
    for time_column, memory_column in zip(time_columns, memory_columns):
        save_name = f"{graph_type}{time_column.split('_')[0]}_memory.png"
        plot_memory_time(summary_data, time_column, memory_column, graph_type, save_path=save_name)

