import networkx
from networkx.readwrite import node_link_data as save_graph
import json
from datetime import datetime
from time import time as tick

from shared import cost, build_depth_first_mst
from generators import no_zero_cost, sparse
from search_algorithms import tabu_search

# PARAMETRI ISTANZA
MAX_NODES = 150
BRANCHING_FACTOR = int(MAX_NODES*0.05)
ROOT_NODE = 7

# PARAMETRI RICERCA
TABU_SIZE = 20      
MAX_ITER = 36000                  # arresta la ricerca dopo queste iterazioni (es. se il grafo è troppo grosso)
MAX_ITER_NO_IMPROVEMENT = 1000    # max. iterazioni su uno stallo




G = sparse(MAX_NODES, m=BRANCHING_FACTOR, seed=191295)

mst = build_depth_first_mst(G, root_node=ROOT_NODE)
#mst = networkx.algorithms.minimum_spanning_tree(G)

# PRINT INFO SOL. INIZIALE
print("Costo iniziale:", cost(mst, ROOT_NODE))

print("")
print("---DETTAGLI---")
V = G.number_of_nodes()
E = G.number_of_edges()
print("|V| = ", V)
print("|E| = ", E)
print("")




print("---INIZIO OTTMIZZAZIONE---")
print("Ottimizzatore: TABU_SEARCH")
print("   TABU_SIZE:",TABU_SIZE)
print("   MAX_ITER:",MAX_ITER)
print("   MAX_ITER_NO_IMPROVEMENT:",MAX_ITER_NO_IMPROVEMENT)

start_time = tick()
results = tabu_search(G, start_solution=mst, ROOT_NODE=ROOT_NODE, 
                        TABU_SIZE=TABU_SIZE, 
                        MAX_ITER=MAX_ITER, MAX_ITER_NO_IMPROVEMENT=MAX_ITER_NO_IMPROVEMENT)
end_time = tick()



mst = results["solution"]
iter = results["elapsed_iterations"]
iters_since_last_improvement = results["since_last_improvement_iterations"]

# PRINT RESULTS
print("Costo finale: ", cost(mst, ROOT_NODE), "(in",(end_time-start_time),"secondi)")
print("MST = ",list(mst.edges))

print("")
print("---DETTAGLI---")
print("Iterazioni complessive eseguite: {}/{}".format(iter,MAX_ITER))
print("Iterazioni eseguite dall'ultimo miglioramento di funzione obiettivo: {}/{}".format(iters_since_last_improvement ,MAX_ITER_NO_IMPROVEMENT))
print("Stallo raggiunto: ", iters_since_last_improvement >= MAX_ITER_NO_IMPROVEMENT)
print("Nodi non ottimali (nodo: n. figli): ",[{n: x-(ROOT_NODE!=n)*1} for (n,x) in mst.degree() if x > 2])
V = G.number_of_nodes()
E = G.number_of_edges()
print("|V| = ", V)
print("|E| = ", E)



# PROVA SALVATAGGIO
timestamp =  datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
filename = "HYBRID-TABU_{}_{}__cost_{}_{}.json".format(V, E, results["cost"], timestamp)
with open("solutions/"+filename, "w+") as f:
    data = save_graph(mst)
    json.dump(data,f)


# PROVA CARICAMENTO
#from networkx.readwrite import node_link_graph as load_graph

#with open("solutions/"+filename, "r") as f:
#    data = json.load(f)
#    mst1 = load_graph(data)
#    print("MST Loaded: ",list(mst1.edges))