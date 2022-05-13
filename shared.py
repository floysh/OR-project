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



# GREEDY

# Creazione di MST con radice specificata tramite visita in ampiezza
def build_rooted_mst(graph, root_node):
    visited_nodes = set() # per evitare cicli
    next_visit = []

    MST = nx.Graph()

    #MST.add_node(n1) # non necessario, aggiunti in automatico con gli archi

    #next_visit = list(G.adj[root_node]) # inserisci i vicini del nodo di partenza

    next_visit.insert(0,root_node) # assicurati di partire dal nodo radice!
    #for n in next_visit:
    while len(next_visit) > 0:
        n = next_visit.pop(0)
        # processa un nodo solo se non è già stato visitato
        if n not in visited_nodes:
            visited_nodes.add(n)
            # aggiungi i suoi vicini non visitati alla lista/stack di visita
            unvisited_neighbourhood = [x for x in list(G.adj[n]) if x not in visited_nodes]
            #print("n = ",n)
            #print("unvisited_neighbourhood = ",unvisited_neighbourhood)
            #print("(before loop) next_visit = ",next_visit)
            # inserimento in testa -> depth first?
            next_visit = unvisited_neighbourhood + next_visit
            for neighbour in unvisited_neighbourhood:
                if neighbour not in MST.nodes:
                    #print("MST edge added: ", (n,neighbour))
                    MST.add_edge(n,neighbour)
            #print("(after loop) next_visit = ",next_visit) 
        #else:
            #print("n = ", n, "(ignored)")

    return MST



# Creazione di MST con radice specificata tramite visita in profondità
def build_depth_first_mst(graph, root_node):
    MST = nx.Graph()
    return __recursive_depth_first(graph, root_node, MST)

def __recursive_depth_first(graph, node, MST):
    # MST è una risorsa condivisa tra le ricorsioni
    # TODO: trovare un modo più elegante di aggiornarlo
    children = graph.adj[node]
    for child in children:
        if child not in MST.nodes:
            MST.add_edge(node, child)
            MST = __recursive_depth_first(graph, child, MST)
    return MST



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