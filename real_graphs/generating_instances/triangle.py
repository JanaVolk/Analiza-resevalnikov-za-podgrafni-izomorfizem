import networkx as nx
import os
from generated_graphs.generating_instances.treeGraphInduced import export_graph_lad, export_graph_ri, export_graph_vf3

def generate_triangle_graph():
    # triangle: nodes 0-1-2-0 
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    return G

def main():
    triangle = generate_triangle_graph()

    out_dir = "triangle"
    os.makedirs(out_dir, exist_ok=True)

    # LAD format (no extension)
    lad_path = os.path.join(out_dir, "triangle")
    export_graph_lad(triangle, lad_path)

    # RI format (.gfu)
    ri_path = os.path.join(out_dir, "triangle.gfu")
    export_graph_ri(triangle, ri_path, "#query")

    # VF3 format (.sub.grf)
    vf3_path = os.path.join(out_dir, "triangle.sub.grf")
    export_graph_vf3(triangle, vf3_path)

    print("Triangle subgraphs exported in LAD, RI, and VF3 formats in the 'triangle' folder.")

if __name__ == "__main__":
    main()