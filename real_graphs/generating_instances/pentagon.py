import networkx as nx
import os
from generated_graphs.generating_instances.treeGraphInduced import export_graph_lad, export_graph_ri, export_graph_vf3

def generate_pentagon_graph():
    # pentagon: nodes 0-1-2-3-4-0
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    return G

def main():
    pentagon = generate_pentagon_graph()

    out_dir = "pentagon"
    os.makedirs(out_dir, exist_ok=True)

    # LAD format (no extension)
    lad_path = os.path.join(out_dir, "pentagon")
    export_graph_lad(pentagon, lad_path)

    # RI format (.gfu)
    ri_path = os.path.join(out_dir, "pentagon.gfu")
    export_graph_ri(pentagon, ri_path, "#query")

    # VF3 format (.sub.grf)
    vf3_path = os.path.join(out_dir, "pentagon.sub.grf")
    export_graph_vf3(pentagon, vf3_path)

    print("Pentagon subgraphs exported in LAD, RI, and VF3 formats in the 'pentagon' folder.")

if __name__ == "__main__":
    main()