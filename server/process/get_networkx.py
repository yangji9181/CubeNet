from networkx.readwrite import json_graph
from networkx import *
import networkx as nx
import json
def get_graph_property(filename):
    with open(filename) as f:
        js_graph = json.load(f)
    G = json_graph.node_link_graph(js_graph)
    return (nx.radius(G), nx.diameter(G), nx.density(G))

