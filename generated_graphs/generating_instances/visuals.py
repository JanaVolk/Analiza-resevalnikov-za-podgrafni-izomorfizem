import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

def generate_tree_graph(num_nodes):
    """Generate minimum spanning tree from complete graph with random weights"""
    G = nx.complete_graph(num_nodes)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    tree = nx.minimum_spanning_tree(G)
    return tree

def generate_scale_free_graph(num_nodes, m):
    """Generate scale-free graph using Barabási-Albert model"""
    return nx.barabasi_albert_graph(num_nodes, m)

def generate_er_graph(num_nodes, p):
    """Generate Erdős-Rényi random graph"""
    return nx.erdos_renyi_graph(n=num_nodes, p=p)

def generate_random_subgraph(G, fraction):
    """Generate connected subgraph using random walk"""
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

def visualize_graph_types():
    """Create visualization of all three graph types with subgraphs"""
    # Set parameters
    num_nodes = 50  # Smaller for better visualization
    
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    
    # Graph types and their parameters
    graph_types = [
        ("Minimalno vpeto drevo", lambda: generate_tree_graph(num_nodes)),
        ("Scale-free (Barabási-Albert)", lambda: generate_scale_free_graph(num_nodes, 2)),
        ("Erdős-Rényi (p=0.1)", lambda: generate_er_graph(num_nodes, 0.1))
    ]
    
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    subgraph_colors = ['darkblue', 'darkgreen', 'darkred']
    
    # Add column labels at the top
    columns = ['Tarča', 'Vzorec 10%', 'Vzorec 20%', 'Vzorec 60%']
    for j, col_name in enumerate(columns):
        axes[0, j].text(0.5, 1.15, col_name, transform=axes[0, j].transAxes,
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    for i, (graph_name, graph_generator) in enumerate(graph_types):
        # Generate main graph
        G = graph_generator()
        
        # Ensure graph is connected for subgraph generation
        if not nx.is_connected(G):
            # Take largest connected component
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc)
        
        # Generate layout for consistent positioning
        pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
        
        # Plot original graph
        ax = axes[i, 0]
        nx.draw(G, pos, ax=ax, node_color=colors[i], node_size=50, 
                with_labels=False, edge_color='gray', width=0.5)
        
        # Add text under the original graph
        ax.text(0.5, -0.15, f'{graph_name}\n({len(G.nodes())} vozlišč, {len(G.edges())} povezav)', 
                transform=ax.transAxes, ha='center', va='top', fontsize=10, fontweight='bold')
        
        # Generate and plot subgraphs of different sizes
        fractions = [0.1, 0.2, 0.6]
        fraction_labels = ["10%", "20%", "60%"]
        
        for j, (fraction, label) in enumerate(zip(fractions, fraction_labels)):
            subgraph = generate_random_subgraph(G, fraction)
            
            ax = axes[i, j+1]
            
            # Draw original graph in light color
            nx.draw(G, pos, ax=ax, node_color='lightgray', node_size=30,
                    with_labels=False, edge_color='lightgray', width=0.3)
            
            # Highlight subgraph
            subgraph_nodes = list(subgraph.nodes())
            subgraph_pos = {node: pos[node] for node in subgraph_nodes}
            
            nx.draw_networkx_nodes(G, pos, nodelist=subgraph_nodes, ax=ax,
                                 node_color=subgraph_colors[i], node_size=60)
            nx.draw_networkx_edges(subgraph, pos, ax=ax,
                                 edge_color=subgraph_colors[i], width=1.5)
            
            # Add text under each subgraph
            ax.text(0.5, -0.15, f'Vzorčni podgraf ({label})\n({len(subgraph.nodes())} vozlišč, {len(subgraph.edges())} povezav)', 
                    transform=ax.transAxes, ha='center', va='top', fontsize=9)
    
    # Remove axes
    for ax in axes.flat:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.15)  # Make room for top and bottom text
    plt.savefig('sintetični_grafi_vzorci.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('sintetični_grafi_vzorci.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_graph_properties():
    """Analyze and print properties of generated graphs"""
    num_nodes = 1000
    
    print("Analiza lastnosti sintetičnih grafov (1000 vozlišč):\n")
    print("=" * 60)
    
    # Generate graphs
    tree = generate_tree_graph(num_nodes)
    scale_free = generate_scale_free_graph(num_nodes, 2)
    er_graph = generate_er_graph(num_nodes, 0.01)
    
    graphs = [
        ("Minimalno vpeto drevo", tree),
        ("Scale-free (Barabási-Albert)", scale_free),
        ("Erdős-Rényi (p=0.01)", er_graph)
    ]
    
    for name, G in graphs:
        print(f"\n{name}:")
        print(f"  Vozlišča: {G.number_of_nodes()}")
        print(f"  Povezave: {G.number_of_edges()}")
        print(f"  Povprečna stopnja: {2 * G.number_of_edges() / G.number_of_nodes():.2f}")
        print(f"  Gostota: {nx.density(G):.4f}")
        
        if nx.is_connected(G):
            print(f"  Premer: {nx.diameter(G)}")
            print(f"  Povprečna razdalja: {nx.average_shortest_path_length(G):.2f}")
            print(f"  Clustering coefficient: {nx.average_clustering(G):.4f}")
        else:
            print(f"  Graf ni povezan - {nx.number_connected_components(G)} komponent")
        
        degrees = [d for n, d in G.degree()]
        print(f"  Min/Max stopnja: {min(degrees)}/{max(degrees)}")

def create_small_examples():
    """Create small example graphs for detailed illustration"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))  # Made slightly taller for bottom text
    
    # Small examples for better visibility
    num_nodes = 15
    
    # Tree
    tree = generate_tree_graph(num_nodes)
    pos1 = nx.spring_layout(tree, seed=42)
    nx.draw(tree, pos1, ax=axes[0], node_color='lightblue', node_size=300,
            with_labels=True, font_size=8, edge_color='gray', width=2)
    axes[0].text(0.5, -0.15, 'Minimalno vpeto drevo\n(15 vozlišč, 14 povezav)', 
                transform=axes[0].transAxes, ha='center', va='top', fontweight='bold')
    
    # Scale-free
    scale_free = generate_scale_free_graph(num_nodes, 2)
    pos2 = nx.spring_layout(scale_free, seed=42)
    nx.draw(scale_free, pos2, ax=axes[1], node_color='lightgreen', node_size=300,
            with_labels=True, font_size=8, edge_color='gray', width=2)
    axes[1].text(0.5, -0.15, f'Scale-free graf\n({num_nodes} vozlišč, {scale_free.number_of_edges()} povezav)', 
                transform=axes[1].transAxes, ha='center', va='top', fontweight='bold')
    
    # Erdős-Rényi  
    er_graph = generate_er_graph(num_nodes, 0.2)  # Higher p for visibility
    pos3 = nx.spring_layout(er_graph, seed=42)
    nx.draw(er_graph, pos3, ax=axes[2], node_color='lightcoral', node_size=300,
            with_labels=True, font_size=8, edge_color='gray', width=2)
    axes[2].text(0.5, -0.15, f'Erdős-Rényi graf (p=0.2)\n({num_nodes} vozlišč, {er_graph.number_of_edges()} povezav)', 
                transform=axes[2].transAxes, ha='center', va='top', fontweight='bold')
    
    for ax in axes:
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Make room for bottom text
    plt.savefig('mali_primeri_grafov.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('mali_primeri_grafov.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Set font for better Slovenian support
    plt.rcParams['font.family'] = ['DejaVu Sans']
    
    print("Generiranje vizualizacij sintetičnih grafov...")
    
    # Create main visualization
    visualize_graph_types()
    
    # Create small examples
    create_small_examples()
    
    # Analyze properties
    analyze_graph_properties()
    
    print("\nVizualizacije shranjene kot:")
    print("- sintetični_grafi_vzorci.pdf/png")
    print("- mali_primeri_grafov.pdf/png")