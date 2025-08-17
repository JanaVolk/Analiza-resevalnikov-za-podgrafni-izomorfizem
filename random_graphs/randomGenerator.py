import networkx as nx
import random
import os

def generate_random_graph(num_nodes, p):
    return nx.gnm_random_graph(num_nodes, int(p * num_nodes * (num_nodes - 1) / 2))

def export_graph_lad(G, file_path):
    n = G.number_of_nodes()
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    with open(file_path, 'w') as f:
        f.write(f"{n}\n")
        for node in range(n):
            neighbors = list(H.neighbors(node))
            if neighbors:
                line = f"{len(neighbors)} " + " ".join(map(str, neighbors)) + "\n"
            else:
                line = "0\n"
            f.write(line)
    print(f"LAD graph exported to {file_path}")

def export_graph_ri(G, file_path, header):
    n = G.number_of_nodes()
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    edges = []
    for u, v in H.edges():
        if u < v:
            edges.append((u, v))
        else:
            edges.append((v, u))
    edges = sorted(set(edges))
    with open(file_path, 'w') as f:
        f.write(f"{header}\n")
        f.write(f"{n}\n")
        for _ in range(n):
            f.write("a\n")
        f.write(f"{len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")
    print(f"RI graph exported to {file_path}")

def export_graph_vf3(G, file_path, node_attr='label', default_node_attr=1):
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    n = H.number_of_nodes()
    with open(file_path, 'w') as f:
        f.write(f"{n}\n")
        for node in range(n):
            attr = H.nodes[node].get(node_attr, default_node_attr)
            f.write(f"{node} {attr}\n")
        for node in range(n):
            neighbors = list(H.neighbors(node))
            f.write(f"{len(neighbors)}\n")
            for neighbor in neighbors:
                f.write(f"{node} {neighbor}\n")
    print(f"VF3 graph exported to {file_path}")

if __name__ == "__main__":
    num_graphs = 100
    n1, n2 = 1000, 100

    lad_dir = "LAD"
    ri_dir = "RI"
    vf3_dir = "VF3"
    os.makedirs(lad_dir, exist_ok=True)
    os.makedirs(ri_dir, exist_ok=True)
    os.makedirs(vf3_dir, exist_ok=True)

    p_sub = random.uniform(0.01, 0.1)
    G_sub = generate_random_graph(n2, p_sub)
    export_graph_lad(G_sub, os.path.join(lad_dir, "subgraph100.lad"))
    export_graph_ri(G_sub, os.path.join(ri_dir, "subgraph100.gfu"), "#query")
    export_graph_vf3(G_sub, os.path.join(vf3_dir, "subgraph100.sub.grf"))

    for i in range(1, num_graphs + 1):
        p1 = random.uniform(0.01, 0.1)
        G1 = generate_random_graph(n1, p1)

        # LAD format
        export_graph_lad(G1, os.path.join(lad_dir, f"{i}_random_graph_1000.lad"))

        # RI format
        export_graph_ri(G1, os.path.join(ri_dir, f"{i}_random_graph_1000.gfu"), "#data")

        # VF3 format
        export_graph_vf3(G1, os.path.join(vf3_dir, f"{i}_random_graph_1000.grf"))