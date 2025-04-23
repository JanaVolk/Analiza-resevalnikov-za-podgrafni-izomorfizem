import networkx as nx
import random
import os

def generate_er_graph(num_nodes, p):
    G = nx.erdos_renyi_graph(n=num_nodes, p=p)
    return G

def generate_random_subgraph(G, fraction):
    num_nodes = max(1, int(fraction * G.number_of_nodes()))
    start_node = random.choice(list(G.nodes()))
    subgraph_nodes = {start_node}

    while len(subgraph_nodes) < num_nodes:
        current_nodes = list(subgraph_nodes)
        node = random.choice(current_nodes)
        neighbors = set(G.neighbors(node)) - subgraph_nodes
        if neighbors:
            subgraph_nodes.add(random.choice(list(neighbors)))
        else:
            continue

    return G.subgraph(subgraph_nodes)

# LAD
def export_graph_lad(G, file_path):

    n = G.number_of_nodes()
    # Relabel nodes to 0..n-1 in sorted order
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

# RI
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
        # By default, label each node "a":
        for _ in range(n):
            f.write("a\n")
        f.write(f"{len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")
    print(f"RI graph exported to {file_path}")

# VF3
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

def generate_multiple_tests_er_lad(num_tests, num_nodes, p):

    out_dir = "er_lad"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i in range(1, num_tests + 1):
        er_graph = generate_er_graph(num_nodes, p)
        original_file_path = os.path.join(out_dir, f"{i}_original_graph")
        export_graph_lad(er_graph, original_file_path)

        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(er_graph, fraction)
            subgraph_file_path = os.path.join(out_dir, f"{i}_subgraph_{label}")
            export_graph_lad(subgraph, subgraph_file_path)

        print(f"ER LAD Test {i} generated with original graph {original_file_path} and its subgraphs.")

    print(f"All {num_tests} ER LAD tests generated successfully.")

def generate_multiple_tests_er_ri(num_tests, num_nodes, p):
 
    out_dir = "er_ri"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i in range(1, num_tests + 1):
        er_graph = generate_er_graph(num_nodes, p)
        target_file_path = os.path.join(out_dir, f"{i}_original_graph.gfu")
        export_graph_ri(er_graph, target_file_path, "#data")

        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(er_graph, fraction)
            pattern_file_path = os.path.join(out_dir, f"{i}_subgraph_{label}.gfu")
            export_graph_ri(subgraph, pattern_file_path, "#query")

        print(f"ER RI Test {i} generated with target {target_file_path} and subgraphs.")

    print(f"All {num_tests} ER RI tests generated successfully.")

def generate_multiple_tests_er_vf3(num_tests, num_nodes, p):

    out_dir = "er_vf3"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i in range(0, num_tests):
        er_graph = generate_er_graph(num_nodes, p)
        target_file_path = os.path.join(out_dir, f"{i}graph.grf")
        export_graph_vf3(er_graph, target_file_path)

        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(er_graph, fraction)
            pattern_file_path = os.path.join(out_dir, f"{i}graph{label}.sub.grf")
            export_graph_vf3(subgraph, pattern_file_path)

        print(f"ER VF3 Test {i} generated with target {target_file_path} and pattern graphs.")

    print(f"All {num_tests} ER VF3 tests generated successfully.")

if __name__ == "__main__":

    num_tests = 2       
    num_nodes = 1000    
    p = 0.01            

    generate_multiple_tests_er_lad(num_tests, num_nodes, p)
    generate_multiple_tests_er_ri(num_tests, num_nodes, p)
    generate_multiple_tests_er_vf3(num_tests, num_nodes, p)
