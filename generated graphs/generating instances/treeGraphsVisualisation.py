import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np


def generate_tree_graph(num_nodes):

    G = nx.complete_graph(num_nodes)
    
    # Assign random weights to the edges
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    
    # Generate a minimum spanning tree, which serves as a random tree
    tree = nx.minimum_spanning_tree(G)
    
    return tree



# Function to generate a random subgraph
def generate_random_connected_subgraph(G, fraction):
    num_nodes = int(fraction * G.number_of_nodes())
    
    # Start with a random node
    start_node = random.choice(list(G.nodes()))
    subgraph_nodes = {start_node}
    
    # Adding neighbors
    while len(subgraph_nodes) < num_nodes:
        current_nodes = list(subgraph_nodes)
        node = random.choice(current_nodes)
        
        # Get neighbors of the chosen node that are not yet in the subgraph
        neighbors = set(G.neighbors(node)) - subgraph_nodes
        if neighbors:
            # Add a random neighbor to the subgraph
            subgraph_nodes.add(random.choice(list(neighbors)))
        else:
            # If no new neighbors are available, choose a different node from the subgraph
            continue
    
    return G.subgraph(subgraph_nodes)

def export_graph_to_lad(G, file_path, total_nodes):
    """
    Exports the graph G in lad format, ensuring a consistent total number of nodes.
    Nodes not present in G are written with zero connections.
    """
    with open(file_path, 'w') as f:
        # Write the total number of nodes
        f.write(f"{total_nodes}\n")
        
        # Iterate over all nodes up to total_nodes
        for node in range(total_nodes):
            if node in G:
                neighbors = list(G.neighbors(node))
                if neighbors:
                    # Write the number of neighbors and each neighbor index
                    line = f"{len(neighbors)} " + " ".join(map(str, neighbors)) + "\n"
                else:
                    # Node exists but has no neighbors
                    line = "0\n"
            else:
                # Node is isolated (not in the subgraph)
                line = "0\n"
            f.write(line)
    
    print(f"Graph exported to {file_path}")



# Ploting
def plot_graph_and_subgraphs(G, subG_1, subG_2, subG_3):
    plt.figure(figsize=(14, 10))

    # Original graph
    plt.subplot(221)
    pos = nx.spring_layout(G)  
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=20, font_size=8)
    plt.title("Original Tree Graph (40 nodes)")

    # The 0.1 size subgraph
    plt.subplot(222)
    pos_1 = nx.spring_layout(subG_1)  
    nx.draw(subG_1, pos_1, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=500, font_size=10)
    plt.title("Connected Subgraph (10% of original)")

    # The 0.2 size subgraph
    plt.subplot(223)
    pos_2 = nx.spring_layout(subG_2)  
    nx.draw(subG_2, pos_2, with_labels=True, node_color='lightcoral', edge_color='gray', node_size=500, font_size=10)
    plt.title("Connected Subgraph (20% of original)")

    # The 0.6 size subgraph
    plt.subplot(224)
    pos_3 = nx.spring_layout(subG_3)  
    nx.draw(subG_3, pos_3, with_labels=True, node_color='lightpink', edge_color='gray', node_size=500, font_size=10)
    plt.title("Connected Subgraph (60% of original)")

    plt.tight_layout()
    
    # Save the plot
    plt.savefig("graph_and_subgraphs.png")
    print("Plot saved as 'graph_and_subgraphs.png'")


# Visualize the tree and connected subgraphs
def run_graph_generation_and_visualization():
    num_nodes = 40  

    tree_graph = generate_tree_graph(num_nodes)
    print(f"Generated a tree graph with {tree_graph.number_of_nodes()} nodes and {tree_graph.number_of_edges()} edges.")

    export_graph_to_lad(tree_graph, 'original_graph', num_nodes)

    subgraph_10 = generate_random_connected_subgraph(tree_graph, 0.1)
    subgraph_20 = generate_random_connected_subgraph(tree_graph, 0.2)
    subgraph_60 = generate_random_connected_subgraph(tree_graph, 0.6)

    print(f"Generated a subgraph with {subgraph_10.number_of_nodes()} nodes and {subgraph_10.number_of_edges()} edges (10%).")
    export_graph_to_lad(subgraph_10, 'subgraph_10', num_nodes)

    print(f"Generated a subgraph with {subgraph_20.number_of_nodes()} nodes and {subgraph_20.number_of_edges()} edges (20%).")
    export_graph_to_lad(subgraph_20, 'subgraph_20', num_nodes)

    print(f"Generated a subgraph with {subgraph_60.number_of_nodes()} nodes and {subgraph_60.number_of_edges()} edges (60%).")
    export_graph_to_lad(subgraph_60, 'subgraph_60', num_nodes)

    plot_graph_and_subgraphs(tree_graph, subgraph_10, subgraph_20, subgraph_60)

if __name__ == "__main__":
    run_graph_generation_and_visualization()
