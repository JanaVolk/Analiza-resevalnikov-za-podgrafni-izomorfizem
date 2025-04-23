import os
import random
import networkx as nx


def load_snap_ego_network(file_path):
    G = nx.read_edgelist(file_path, nodetype=int)
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

# RI format
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

# VF3 format
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

### function that generates subgraph tests from SNAP graphs ###

def generate_subgraph_tests_from_snap(snap_folder, solver_format='lad', fractions=[0.1, 0.2, 0.6], out_folder="snap_subgraphs"):
    """
    1. Scans snap_folder for all .edges files, 
    2. loads each graph, 
    3. generates subgraphs for each fraction in 'fractions', 
    4. exports them in the chosen solver format.

    """
    output_dir = os.path.join(snap_folder, out_folder)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output folder: {output_dir}")
    
    for filename in os.listdir(snap_folder):
        if filename.endswith(".edges"):
            file_path = os.path.join(snap_folder, filename)
            # Load the original SNAP graph.
            G = load_snap_ego_network(file_path)
            base_name = os.path.splitext(filename)[0]
            
            # Export the original graph in the chosen format.
            if solver_format.lower() == 'lad':
                orig_out = os.path.join(output_dir, base_name + "_original.lad")
                export_graph_lad(G, orig_out)
            elif solver_format.lower() == 'ri':
                orig_out = os.path.join(output_dir, base_name + "_original.gfu")
                export_graph_ri(G, orig_out, "#data")
            elif solver_format.lower() == 'vf3':
                orig_out = os.path.join(output_dir, base_name + "_original.grf")
                export_graph_vf3(G, orig_out)
            else:
                print(f"Unknown solver format: {solver_format}")
                continue
            
            # For each specified fraction, generate and export a connected subgraph.
            for fraction in fractions:
                label = str(int(fraction * 100))  # e.g. 10 for 0.1, 20 for 0.2, etc.
                subG = generate_random_subgraph(G, fraction)
                if solver_format.lower() == 'lad':
                    out_file = os.path.join(output_dir, f"{base_name}_subgraph_{label}.lad")
                    export_graph_lad(subG, out_file)
                elif solver_format.lower() == 'ri':
                    out_file = os.path.join(output_dir, f"{base_name}_subgraph_{label}.gfu")
                    export_graph_ri(subG, out_file, "#query")
                elif solver_format.lower() == 'vf3':
                    out_file = os.path.join(output_dir, f"{base_name}_subgraph_{label}.grf")
                    export_graph_vf3(subG, out_file)
                print(f"Subgraph for fraction {fraction} exported as {out_file}")
    
    print("Subgraph tests generated successfully.")


if __name__ == "__main__":
    snap_folder = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/twitter"

    chosen_format = 'lad'
    
    fractions = [0.1, 0.2, 0.6]

    out_folder = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/SNAP_twitter_lad"
    
    print(f"Processing SNAP files in {snap_folder} to generate subgraphs in {chosen_format.upper()} format.")
    generate_subgraph_tests_from_snap(snap_folder, solver_format=chosen_format, fractions=fractions, out_folder=out_folder)
