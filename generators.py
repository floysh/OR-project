import networkx as nx
#from networkx import graph_atlas, barabasi_albert_graph, complete_graph
from random import seed as set_seed, randint
import time


# CREAZIONE GRAFO e strutture

# Grafo con tanti archi
def dense(n, seed=None, **kwargs):
    if seed == None:
        print("[WARN] Random seed non impostato. Verrà scelto a caso")
        
    G = nx.barabasi_albert_graph(n=n, m=int(n/5), seed=seed)
    
    # Rendiamo il grafo non completo
    G.remove_edges_from([ (1,4), (3,6), (5,3), (4,5)])
    G.remove_edges_from([ 
        (a,b) for a in range(n, int(n/2))
            for b in [x for x in range(1,n-1) if (b+a) %3 != 0]
    ])
    return G

# Grafo con non tanti archi
# buon benchmark, non troppo lento, non troppo semplice da risolvere
def sparse(n,m=3,seed=None):
    if seed == None:
        print("[WARN] Random seed non impostato. Verrà scelto a caso")
        
    G = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    return G


# Grafo che non ha il percorso ottimo di costo 0
def no_zero_cost(max_nodes, seed):
    G = nx.barabasi_albert_graph(n=int(max_nodes/2), m=6, seed=seed)

    # Rendi impossibile trovare un percorso di lunghezza 0
    # aggiungendo nodi raggiungibili solo da uno stesso nodo
    n = len(G.nodes)
    #G.add_edges_from([(ROOT_NODE,x) for x in range(n, n + 5)]) # dummy

    # v.2 by prof. Nonato
    # come sopra ma pensato meglio
    n_0 = n
    star_count = 0
    set_seed(seed)
    while n < max_nodes:
        n_star = min(max_nodes-n,5)     # /!\ non superare il limite di nodi!
        star = nx.generators.star_graph(range(n,n+n_star))
        link_node = randint(0,n_0)      # non attaccare tutte le stelle allo stesso nodo!
        G.add_edges_from(star.edges)    # aggiungi la stella la grafo
        G.add_edge(link_node, n)        # attaccala a un nodo esistente, così G resta connesso!

        n += n_star
        star_count += 1

    print("[INFO] Aggiunte ",star_count, " stelle al grafo di partenza.")
    
    return G



# Switcher unificato
def generate_graph(GRAPH_GENERATOR, MAX_NODES, branching_factor=3, seed=None):

    match GRAPH_GENERATOR:

        case "NX_COMPLETE":
            # Grafo completo -> Ha sicuramente il ciclo hamiltoniano come soluzione ottima
            # (usare per vedere se algoritmo riesce a raggiungere questo pto di ottimo)
            print("[INFO] Uso generatore grafo completo (n={})".format(MAX_NODES))
            G = nx.complete_graph(range(1,MAX_NODES+1))
            return G

        case "NX_DENSE":
            # Grafo denso -> tanti archi
            # per testare performance con tanti archi
            n = MAX_NODES
            m = branching_factor #2*int(n*(n-2)/3)
            print("[INFO] Uso generatore grafo denso (n={}, m={})".format(n,m))
            if seed == None:
                print("[WARN] Random seed non impostato. Verrà scelto a caso")
                
            G = nx.dense_gnm_random_graph(n, m, seed=seed)
            return G

        case "NX_RANDOM":
            if seed == None:
                print("[WARN] Random seed non impostato. Verrà scelto a caso")
            G = nx.random_regular_graph(d=MAX_NODES%10, n=MAX_NODES, seed=seed)
            return G

        
        case "DENSE":
            # [OLD] Generatore grafo denso mio
            # solo legacy, potature non proprio il massimo
            print("[INFO] Uso generatore mio DENSE")
            G = nx.Graph()
            G.add_nodes_from([
                x for x in range(1, MAX_NODES+1)
            ])

            G.add_edges_from([
                (x,y) for x in range(1, MAX_NODES+1)
                        for y in range(x+1, MAX_NODES+1)
            ])

            # Rendiamo il grafo non completo
            G.remove_edges_from([ (1,4), (3,6), (5,3), (4,5)])
            G.remove_edges_from([ 
                (a,b) for a in range(MAX_NODES, int(MAX_NODES/2))
                    for b in [x for x in range(1,MAX_NODES-1) if (b+a) %3 != 0]
            ])
            return G

        case "SPARSE":
            n = MAX_NODES
            m = branching_factor #3#3*int(n*(n/2)/10)

            print("[INFO] Uso generatore SPARSE (Barabasi-Albert, n={}, m={})".format(n,m))
            G = sparse(n=n, m=branching_factor, seed=seed)
            return G

        case "NOT_BEST_PATH":
            print("[INFO] Uso generatore di grafi a stella NOT_BEST_PATH")
            G = no_zero_cost(MAX_NODES, seed)
            return G

            
        case _:
            # robetta semplice
            atlas_num = 1234
            print("[WARN] Nome generatore non valido, uso grafo di test (nx.atlas, id=1234)")
            G = nx.graph_atlas(atlas_num)
            return G
