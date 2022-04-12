import os
import networkx as nx
import matplotlib.pyplot as plt

if not "OUT_DIR" in globals():
    OUT_DIR = "./out"


# Funzione obiettivo

def cost(MST, root_node, debug=False):

    if debug:
        print("root node: ",root_node)

    support_graph = nx.Graph()

    visited = set()
    next = [root_node]
    
    cost = 0

    while len(next) > 0:
        node = next.pop(0)
        node_edges = MST.edges(node)
        
        if node not in visited:
            k_children = len( [ x for x in node_edges if x not in support_graph.edges ] )

            if debug:
                print("node {} has {} children".format(node, k_children))

            if k_children > 1:
                cost += k_children - 1

            visited.add(node)
            next = next + list(MST.adj[node])
            support_graph.add_edges_from(node_edges)
        
    return cost






# Alcune funzioni di supporto

def draw_graph(G, MST=nx.empty_graph(), root_node=None):
    # adapted from:
    # https://stackoverflow.com/questions/60164893/highlighting-certain-nodes-edges-in-networkx-issues-with-using-zip

    nodes_shared_options = {"node_size": 500, "edgecolors": "black", "linewidths": 1.2}
    edges_shared_options = {"connectionstyle": 'arc3', "width": 1.25} 
    
    # Get position using spring layout
    pos = nx.spring_layout(G, seed=54321)
    #pos = nx.circular_layout(G)

    # Get MST path
    path_edges = list(MST.edges)

    # Prepare the figure size
    N = G.number_of_nodes()
    plt.figure(figsize=(max(8,N/6),max(8,N/6)))

    # Draw nodes and edges not included in the MST path
    #nx.draw_networkx_nodes(G, pos, nodelist=set(G.nodes)-set(MST.nodes))
    nx.draw_networkx_nodes(G, pos, nodelist=G.nodes, node_color="whitesmoke", **nodes_shared_options)
    nx.draw_networkx_edges(G, pos, edgelist=set(G.edges)-set(path_edges), edge_color='gray', **edges_shared_options )

    # Draw MST path
    # highlight the root node
    if root_node != None:
        nx.draw_networkx_nodes(G, pos, nodelist=[root_node], node_color='tab:red', **nodes_shared_options)

    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', **edges_shared_options)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_color='black', font_weight='bold')
    nx.draw_networkx_labels(G, pos, labels={root_node: root_node}, font_color='whitesmoke', font_weight='bold')



def save_figure(name, format="svg"):
    filename = "{}.{}".format(name,format)
    plt.tight_layout(pad=1)
    plt.savefig(os.path.join(OUT_DIR,filename), bbox_inches='tight', format=format, dpi=800, transparent=True)