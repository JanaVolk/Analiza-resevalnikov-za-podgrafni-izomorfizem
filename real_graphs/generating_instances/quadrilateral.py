import networkx as nx
import os
from generated_graphs.generating_instances.treeGraphInduced import export_graph_lad, export_graph_ri, export_graph_vf3

def generate_quadrilateral_graph():
    # quadrilateral: nodes 0-1-2-3-0 
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
    return G

def main():
    quad = generate_quadrilateral_graph()

    out_dir = "quadrilateral"
    os.makedirs(out_dir, exist_ok=True)

    # LAD format (no extension)
    lad_path = os.path.join(out_dir, "quadrilateral")
    export_graph_lad(quad, lad_path)

    # RI format (.gfu)
    ri_path = os.path.join(out_dir, "quadrilateral.gfu")
    export_graph_ri(quad, ri_path, "#query")

    # VF3 format (.sub.grf)
    vf3_path = os.path.join(out_dir, "quadrilateral.sub.grf")
    export_graph_vf3(quad, vf3_path)

    print("Quadrilateral subgraphs exported in LAD, RI, and VF3 formats in the 'quadrilateral' folder.")

if __name__ == "__main__":
    main()