import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

def generate_tree_graph(num_nodes):
    G = nx.complete_graph(num_nodes)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    return nx.minimum_spanning_tree(G)

def generate_scale_free_graph(num_nodes, m):
    return nx.barabasi_albert_graph(num_nodes, m)

def generate_er_graph(num_nodes, p):
    return nx.erdos_renyi_graph(n=num_nodes, p=p)

def generate_random_subgraph(G, fraction):
    num_nodes = max(1, int(fraction * G.number_of_nodes()))
    start_node = random.choice(list(G.nodes()))
    subgraph_nodes = {start_node}
    while len(subgraph_nodes) < num_nodes:
        node = random.choice(list(subgraph_nodes))
        neighbors = set(G.neighbors(node)) - subgraph_nodes
        if neighbors:
            subgraph_nodes.add(random.choice(list(neighbors)))
    return G.subgraph(subgraph_nodes)

def visualize_single_graph(graph_name, generator, color, subgraph_color, filename):
    random.seed(42)
    np.random.seed(42)
    num_nodes = 50

    G = generator()
    if not nx.is_connected(G):
        largest_cc = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest_cc)

    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

    fig, axes = plt.subplots(1, 4, figsize=(18, 6))

    # Column labels
    columns = ['Tarča', 'Vzorec 10%', 'Vzorec 20%', 'Vzorec 60%']
    for j, col_name in enumerate(columns):
        axes[j].text(0.5, 1.08, col_name, transform=axes[j].transAxes,
                     ha='center', va='bottom', fontsize=22, fontweight='bold')

    # Original graph
    nx.draw(G, pos, ax=axes[0], node_color=color, node_size=80,
            with_labels=False, edge_color='gray', width=0.8)
    axes[0].text(0.5, -0.15, f'{graph_name}\n({len(G.nodes())} vozlišč, {len(G.edges())} povezav)',
                 transform=axes[0].transAxes, ha='center', va='top', fontsize=20, fontweight='bold')

    # Subgraphs
    fractions = [0.1, 0.2, 0.6]
    labels = ["10%", "20%", "60%"]

    for j, (fraction, label) in enumerate(zip(fractions, labels)):
        subgraph = generate_random_subgraph(G, fraction)
        nx.draw(G, pos, ax=axes[j+1], node_color='lightgray', node_size=40,
                with_labels=False, edge_color='lightgray', width=0.3)
        nx.draw_networkx_nodes(G, pos, nodelist=subgraph.nodes(), ax=axes[j+1],
                               node_color=subgraph_color, node_size=100)
        nx.draw_networkx_edges(subgraph, pos, ax=axes[j+1],
                               edge_color=subgraph_color, width=2)
        axes[j+1].text(0.5, -0.15, f'Vzorčni podgraf ({label})\n({len(subgraph.nodes())} vozlišč, {len(subgraph.edges())} povezav)',
                       transform=axes[j+1].transAxes, ha='center', va='top', fontsize=18)

    # Clean up
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')

    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.2)
    plt.savefig(f'{filename}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'{filename}.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    plt.rcParams['font.family'] = ['DejaVu Sans']

    visualize_single_graph(
        "Minimalno vpeto drevo",
        lambda: generate_tree_graph(50),
        "lightblue", "darkblue",
        "mst_graph"
    )
    visualize_single_graph(
        "Scale-free (Barabási-Albert)",
        lambda: generate_scale_free_graph(50, 2),
        "lightgreen", "darkgreen",
        "scale_free_graph"
    )
    visualize_single_graph(
        "Erdős-Rényi (p=0.1)",
        lambda: generate_er_graph(50, 0.1),
        "lightcoral", "darkred",
        "er_graph"
    )
