import osmnx as ox
from osmnx.distance import add_edge_lengths
from osmnx.plot import get_edge_colors_by_attr
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#Get graph from bbox
graph = ox.graph_from_bbox(55.3002, 54.9855, 14.6770, 15.1604, network_type='drive')


add_edge_lengths(graph)

fig, ax = ox.plot_graph(graph, show=False, close=False)

for _, edge in ox.graph_to_gdfs(graph, nodes=False).fillna("NaN").iterrows():
    text = edge["length"]
    c = edge["geometry"].centroid
    ax.annotate(text, (c.x, c.y), c="y")

plt.show()
