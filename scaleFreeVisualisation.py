import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

n = 1000
m = 2

# BA (Barabási–Albert) scale-free graph
G = nx.barabasi_albert_graph(n, m)

degree_sequence = [d for _, d in G.degree()]
degree_counts = Counter(degree_sequence)

print("Graph degree distribution:")
print("power\tnum")
for degree, count in sorted(degree_counts.items()):
    print(f"{degree}\t{count}")


fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Subplot 1: graph
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos=pos, node_size=20, with_labels=False, ax=axs[0])
axs[0].set_title("BA Scale-Free Graph")
axs[0].axis("off")

# Subplot 2: degree distribution as a bar chart
degrees = sorted(degree_counts.keys())
counts = [degree_counts[d] for d in degrees]
axs[1].bar(degrees, counts, color="skyblue")
axs[1].set_xlabel("Degree (Power)")
axs[1].set_ylabel("Number of Nodes")
axs[1].set_title("Degree Distribution")

plt.tight_layout()
plt.show()
