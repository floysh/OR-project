from time import time as tick

from shared import cost, build_depth_first_mst
from generators import no_zero_cost, sparse
from search_algorithms import local_search

# PARAMETRI ISTANZA
MAX_NODES = 150
BRANCHING_FACTOR = int(MAX_NODES*0.05)
ROOT_NODE = 7

# PARAMETRI RICERCA
MAX_ITER = 36000    # arresta la ricerca dopo queste iterazioni 
                    # (es. se il grafo è troppo grosso)




G = sparse(MAX_NODES, m=BRANCHING_FACTOR, seed=191295)

mst = build_depth_first_mst(G, root_node=ROOT_NODE)

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
print("Ottimizzatore: LOCAL_SEARCH")
print("   MAX_ITER:",MAX_ITER)

start_time = tick()
results = local_search(G, start_solution=mst, ROOT_NODE=ROOT_NODE, MAX_ITER=MAX_ITER)
end_time = tick()



mst = results["solution"]
iter = results["elapsed_iterations"]
iters_since_last_improvement = results["since_last_improvement_iterations"]

# PRINT RESULTS
print("Costo finale: ", cost(mst, ROOT_NODE), "(in",(end_time-start_time),"secondi)")

print("")
print("---DETTAGLI---")
print("Costo finale: ", cost(mst, ROOT_NODE))
print("Tempo di esecuzione: ",(end_time-start_time),"secondi")
print("Iterazioni complessive eseguite: {}/{}".format(iter,MAX_ITER))
print("Nodi non ottimali (nodo: n. figli): ",[{n: x-(ROOT_NODE!=n)*1} for (n,x) in mst.degree() if x > 2])
V = G.number_of_nodes()
E = G.number_of_edges()
print("|V| = ", V)
print("|E| = ", E)