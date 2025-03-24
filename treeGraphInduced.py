import networkx as nx
import random
import os

# Generates a minimum spanning tree from a complete graph with random edge weights
def generate_tree_graph(num_nodes):
    G = nx.complete_graph(num_nodes)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    tree = nx.minimum_spanning_tree(G)
    return tree

# Generates a connected subgraph with a given fraction of nodes
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

# LAD format
def export_graph_lad(G, file_path):
    """
      - the first line contains n number of nodes
      - for each node (indexed from 0 to n-1 in sorted order):
          * if the node has neighbors, the line starts with k (the number of neighbors)
            followed by k space-separated neighbor node indices.
          * if the node has no neighbors, the line contains just "0"
    """
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
    print(f"Graph exported to {file_path}")

def export_graph_ri(G, file_path, header):
    """
        - first line is header "#data" or "#query"
        - next line contains number of vertices
        - then vertex label for vertex 0
            vertex label for vertex 1 
        ...
            vertex label for vertex n-1
        - then number of all edges
        - every edge: u v
    """
    n = G.number_of_nodes()
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    
    # For undirected graphs each edge once (with u < v).
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
        # "a" by default
        for _ in range(n):
            f.write("a\n")
        f.write(f"{len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")
    print(f"RI graph exported to {file_path}")


def export_graph_vf3(G, file_path, node_attr='label', default_node_attr=1):
    """
      - first line is the number of vertices (n)
      - next n lines contain the vertex id and its attribute, one per line
        for example:
            0 1
            1 1
            2 1
            ... 
      - then, for each vertex (from 0 to n-1), a block:
          * first, a line with the number of neighbors of that vertex
          * then, one line per neighbor in the format "u v" (where u is the current vertex)
    
    for undirected graphs, each edge appears in the block for both endpoints
    """
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

# LAD and Glasgow solvers
def generate_multiple_tests(num_tests, num_nodes):
    out_dir = "test_instances_induced_g_l"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for i in range(1, num_tests + 1):
        tree_graph = generate_tree_graph(num_nodes)
        original_file_path = os.path.join(out_dir, f"{i}_original_graph")
        export_graph_lad(tree_graph, original_file_path)

        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(tree_graph, fraction)
            subgraph_file_path = os.path.join(out_dir, f"{i}_subgraph_{label}")
            export_graph_lad(subgraph, subgraph_file_path)
    
        print(f"Test {i} generated with files {original_file_path} and corresponding subgraphs.")
    
    print(f"All {num_tests} LAD tests generated successfully.")

# RI solver
def generate_multiple_tests_ri(num_tests, num_nodes):
    out_dir = "test_instances_ri"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for i in range(1, num_tests + 1):
        tree_graph = generate_tree_graph(num_nodes)
        target_file_path = os.path.join(out_dir, f"{i}_original_graph.gfu")
        export_graph_ri(tree_graph, target_file_path, "#data")

        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(tree_graph, fraction)
            pattern_file_path = os.path.join(out_dir, f"{i}_subgraph_{label}.gfu")
            export_graph_ri(subgraph, pattern_file_path, "#query")
    
        print(f"Test {i} generated with target {target_file_path} and corresponding pattern graphs.")
    
    print(f"All {num_tests} RI tests generated successfully.")

# VF3 solver
def generate_multiple_tests_vf3(num_tests, num_nodes):
    out_dir = "test_instances_vf3_800"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for i in range(1, num_tests + 1):
        tree_graph = generate_tree_graph(num_nodes)
        target_file_path = os.path.join(out_dir, f"{i}graph.grf")
        export_graph_vf3(tree_graph, target_file_path)
        
        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_subgraph(tree_graph, fraction)
            pattern_file_path = os.path.join(out_dir, f"{i}graph{label}.sub.grf")
            export_graph_vf3(subgraph, pattern_file_path)
    
        print(f"Test {i} generated with target {target_file_path} and corresponding VF3 pattern graphs.")
    
    print(f"All {num_tests} VF3 tests generated successfully.")


if __name__ == "__main__":

    generate_multiple_tests(num_tests=2, num_nodes=1000)
    
    generate_multiple_tests_ri(num_tests=2, num_nodes=1000)

    generate_multiple_tests_vf3(num_tests=2, num_nodes=1000)
