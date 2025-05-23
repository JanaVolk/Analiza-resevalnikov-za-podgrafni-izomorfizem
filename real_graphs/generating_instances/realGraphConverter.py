import os
import networkx as nx

def read_snap_graph(file_path):
    G = nx.Graph()
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            u, v = map(int, parts[:2])
            G.add_edge(u, v)
    return G

def export_graph_lad(G, file_path):
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    with open(file_path, 'w') as f:
        f.write(f"{H.number_of_nodes()}\n")
        for node in range(H.number_of_nodes()):
            neighbors = sorted(H.neighbors(node))
            line = f"{len(neighbors)} {' '.join(map(str, neighbors))}\n" if neighbors else "0\n"
            f.write(line)

def export_graph_ri(G, file_path, header="#data"):
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    edges = {(min(u, v), max(u, v)) for u, v in H.edges()}
    edges = sorted(edges)
    with open(file_path, 'w') as f:
        f.write(f"{header}\n{H.number_of_nodes()}\n")
        f.writelines("a\n" for _ in range(H.number_of_nodes()))
        f.write(f"{len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")

def export_graph_vf3(G, file_path, node_attr=1):
    mapping = {old: new for new, old in enumerate(sorted(G.nodes()))}
    H = nx.relabel_nodes(G, mapping)
    with open(file_path, 'w') as f:
        f.write(f"{H.number_of_nodes()}\n")
        for node in range(H.number_of_nodes()):
            f.write(f"{node} {node_attr}\n")
        for node in range(H.number_of_nodes()):
            neighbors = sorted(H.neighbors(node))
            f.write(f"{len(neighbors)}\n")
            for neighbor in neighbors:
                f.write(f"{node} {neighbor}\n")

def export_real_graphs_from_folder(snap_folder, out_folder_prefix="real_graphs"):
    for filename in os.listdir(snap_folder):
        if filename.endswith(".edges"):
            file_path = os.path.join(snap_folder, filename)
            base_name = os.path.splitext(filename)[0]
            G = read_snap_graph(file_path)
            # LAD
            lad_dir = os.path.join(snap_folder, f"{out_folder_prefix}_lad")
            os.makedirs(lad_dir, exist_ok=True)
            export_graph_lad(G, os.path.join(lad_dir, base_name + ".lad"))
            # RI
            ri_dir = os.path.join(snap_folder, f"{out_folder_prefix}_ri")
            os.makedirs(ri_dir, exist_ok=True)
            export_graph_ri(G, os.path.join(ri_dir, base_name + ".gfu"), "#data")
            # VF3
            vf3_dir = os.path.join(snap_folder, f"{out_folder_prefix}_vf3")
            os.makedirs(vf3_dir, exist_ok=True)
            export_graph_vf3(G, os.path.join(vf3_dir, base_name + ".grf"))
    print("All .edges real graphs exported successfully.")

def export_real_graphs_from_dict(snap_file_paths):
    for snap_file_path, output_dir in snap_file_paths.items():
        print(f"\nProcessing {snap_file_path}...")
        G = read_snap_graph(snap_file_path)
        # LAD
        lad_dir = os.path.join(output_dir, "lad")
        os.makedirs(lad_dir, exist_ok=True)
        export_graph_lad(G, os.path.join(lad_dir, "full_graph.lad"))
        # RI
        ri_dir = os.path.join(output_dir, "ri")
        os.makedirs(ri_dir, exist_ok=True)
        export_graph_ri(G, os.path.join(ri_dir, "full_graph.gfu"), "#data")
        # VF3
        vf3_dir = os.path.join(output_dir, "vf3")
        os.makedirs(vf3_dir, exist_ok=True)
        export_graph_vf3(G, os.path.join(vf3_dir, "0graph.grf"))
    print("All .txt real graphs exported successfully.")

if __name__ == "__main__":
    # .edges files
    snap_folder = "/home/jana/Documents/DIPLOMA/AAA/Analiza-resevalnikov-za-podgrafni-izomorfizem/twitter"
    export_real_graphs_from_folder(snap_folder, out_folder_prefix="real_graphs")

    # .txt files
    snap_file_paths = {

        # Networks with ground-truth communities)
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/com-orkut.ungraph.txt": "com-orkut_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/com-amazon.ungraph.txt": "com-amazon_tests",

        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/email-Eu-core-department-labels.txt": "email-Eu-core-department-labels.txt",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/email-Eu-core.txt": "email-Eu-core.txt",

        # Communication networks 
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/Email-Enron.txt": "email-enron_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/Email-EuAll.txt": "email-euall_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/5sklop/WikiTalk.txt": "wikitalk_tests",

        # Citation networks
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Cit-HepPh.txt":     "Cit-HepPh_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Cit-HepTh.txt":     "Cit-HepTh_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/cit-Patents.txt":   "cit-Patents_tests",

        # Collaboration networks
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/CA-AstroPh.txt": "CA-AstroPh_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/CA-CondMat.txt": "CA-rCondMat_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/CA-GrQc.txt": "CA-GrQc_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/CA-HepPh.txt": "CA-HepPh_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/CA-HepTh.txt": "CA-HepTh_tests",

        # Web graphs
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/web-BerkStan.txt": "web-BerkStan_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/web-Google.txt": "web-Google_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/web-NotreDame.txt": "web-NotreDame_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/web-Stanford.txt": "web-Stanford_tests",

        # Product co-purchasing networks (Amazon)
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Amazon0302.txt": "Amazon0302_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Amazon0312.txt": "Amazon0312_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Amazon0505.txt": "Amazon0505_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Amazon0601.txt": "Amazon0601_tests",

        # Internet peer-to-peer networks
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella04.txt": "p2p-Gnutella04_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella05.txt": "p2p-Gnutella05_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella06.txt": "p2p-Gnutella06_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella08.txt": "p2p-Gnutella08_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella09.txt": "p2p-Gnutella09_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella24.txt": "p2p-Gnutella24_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella25.txt": "p2p-Gnutella25_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/p2p-Gnutella30.txt": "p2p-Gnutella30_tests",

        # Autonomous systems graphs
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as20000102.txt": "as20000102_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-skitter.txt": "as-skitter_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010331.txt": "oregon1_010331_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010407.txt": "oregon1_010407_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010414.txt": "oregon1_010414_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010421.txt": "oregon1_010421_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010428.txt": "oregon1_010428_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010505.txt": "oregon1_010505_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010512.txt": "oregon1_010512_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon1_010519.txt": "oregon1_010519_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010331.txt": "oregon2_010331_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010407.txt": "oregon2_010407_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010414.txt": "oregon2_010414_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010421.txt": "oregon2_010421_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010428.txt": "oregon2_010428_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010505.txt": "oregon2_010505_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010512.txt": "oregon2_010512_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010519.txt": "oregon2_010519_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/oregon2_010526.txt": "oregon2_010526_tests",

        ## as-733
        # Autonomous systems graphs (AS-733) 

        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971108.txt": "as19971108_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971109.txt": "as19971109_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971110.txt": "as19971110_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971111.txt": "as19971111_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971112.txt": "as19971112_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971113.txt": "as19971113_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971114.txt": "as19971114_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971115.txt": "as19971115_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971116.txt": "as19971116_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971117.txt": "as19971117_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971118.txt": "as19971118_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971119.txt": "as19971119_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971120.txt": "as19971120_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971121.txt": "as19971121_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971122.txt": "as19971122_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971123.txt": "as19971123_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971124.txt": "as19971124_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971125.txt": "as19971125_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971126.txt": "as19971126_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971127.txt": "as19971127_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971128.txt": "as19971128_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971129.txt": "as19971129_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971130.txt": "as19971130_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971201.txt": "as19971201_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971202.txt": "as19971202_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971203.txt": "as19971203_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971204.txt": "as19971204_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971205.txt": "as19971205_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971206.txt": "as19971206_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971207.txt": "as19971207_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971208.txt": "as19971208_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971209.txt": "as19971209_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971210.txt": "as19971210_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971211.txt": "as19971211_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971212.txt": "as19971212_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971213.txt": "as19971213_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971214.txt": "as19971214_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971215.txt": "as19971215_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971216.txt": "as19971216_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971217.txt": "as19971217_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971218.txt": "as19971218_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971219.txt": "as19971219_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971220.txt": "as19971220_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971221.txt": "as19971221_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971222.txt": "as19971222_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971223.txt": "as19971223_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971224.txt": "as19971224_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971225.txt": "as19971225_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971226.txt": "as19971226_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/6sklop/as-733/as19971227.txt": "as19971227_tests",

        # Location-based online social networks
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Brightkite_edges.txt": "Brightkite_edges_tests",
        "/home/jana/Documents/DIPLOMA/REAL TESTI/3sklop/Gowalla_edges.txt": "Gowalla_edges_tests"
    }
    if snap_file_paths:
        export_real_graphs_from_dict(snap_file_paths)