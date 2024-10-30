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
def generate_random_connected_subgraph(G, fraction):

    num_nodes = int(fraction * G.number_of_nodes())
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

# Exports the graph G in lad format
def export_graph_to_lad(G, file_path, total_nodes):

    with open(file_path, 'w') as f:
        f.write(f"{total_nodes}\n")
        for node in range(total_nodes):
            if node in G:
                neighbors = list(G.neighbors(node))
                if neighbors:
                    line = f"{len(neighbors)} " + " ".join(map(str, neighbors)) + "\n"
                else:
                    line = "0\n"
            else:
                line = "0\n"
            f.write(line)
    print(f"Graph exported to {file_path}")

# Generates multiple original and subgraph pairs in lad format for testing
def generate_multiple_tests(num_tests, num_nodes):

    if not os.path.exists("test_instances"):
        os.makedirs("test_instances")
    
    for i in range(1, num_tests + 1):
        # Generate original graph
        tree_graph = generate_tree_graph(num_nodes)
        original_file_path = f"test_instances/{i}_original_graph"
        export_graph_to_lad(tree_graph, original_file_path, num_nodes)
        
        # Generate subgraphs with different fractions of nodes
        for fraction, label in zip([0.1, 0.2, 0.6], ["10", "20", "60"]):
            subgraph = generate_random_connected_subgraph(tree_graph, fraction)
            subgraph_file_path = f"test_instances/{i}_subgraph_{label}"
            export_graph_to_lad(subgraph, subgraph_file_path, num_nodes)

        print(f"Test {i} generated with files {original_file_path} and corresponding subgraphs.")
    
    print(f"All {num_tests} tests generated successfully.")

if __name__ == "__main__":
    generate_multiple_tests(num_tests=100, num_nodes=1000)
