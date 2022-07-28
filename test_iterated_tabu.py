import networkx
from networkx.readwrite import node_link_data as save_graph
import json
from datetime import datetime
from time import time as tick

from shared import cost, build_depth_first_mst
from generators import no_zero_cost, sparse, dense
from search_algorithms import tabu_search

# PARAMETRI ISTANZA
RANDOM_SEED = 191295
MAX_NODES = 150
BRANCHING_FACTOR = int(MAX_NODES*0.05)
ROOT_NODE = 7

# PARAMETRI RICERCA
TABU_SIZE = 15
MAX_RESTART = 5
MAX_ITER = 5000                  # arresta la ricerca dopo queste iterazioni (es. se il grafo è troppo grosso)
MAX_ITER_BEFORE_ASCEND = 350
MAX_ITER_NO_IMPROVEMENT = 500    # max. iterazioni su uno stallo

DIVERSIFICATION_BATCH_SIZE = 3




G = sparse(MAX_NODES, m=BRANCHING_FACTOR, seed=RANDOM_SEED)

#mst = build_depth_first_mst(G, root_node=ROOT_NODE)
mst = networkx.algorithms.minimum_spanning_tree(G)

# ottimo locale (costo 7)
#mst = networkx.Graph()
#mst.add_edges_from([(7, 139), (0, 118), (0, 132), (1, 77), (1, 117), (9, 143), (9, 139), (4, 60), (4, 144), (8, 12), (8, 94), (2, 10), (10, 119), (10, 98), (5, 134), (5, 92), (11, 3), (11, 100), (3, 55), (12, 129), (6, 121), (6, 127), (13, 31), (13, 117), (14, 23), (21, 39), (21, 123), (17, 22), (17, 146), (15, 113), (15, 124), (16, 122), (16, 48), (18, 46), (18, 105), (22, 33), (23, 75), (23, 110), (24, 29), (25, 99), (25, 115), (26, 141), (26, 146), (58, 27), (58, 43), (32, 28), (32, 120), (28, 40), (40, 36), (36, 61), (37, 33), (37, 129), (39, 46), (39, 51), (39, 130), (57, 34), (57, 41), (34, 29), (19, 126), (19, 49), (31, 44), (31, 49), (44, 41), (30, 38), (30, 128), (38, 140), (48, 35), (35, 47), (47, 43), (43, 20), (43, 45), (20, 50), (50, 56), (56, 59), (59, 73), (73, 42), (42, 76), (76, 65), (65, 125), (125, 96), (96, 106), (106, 104), (104, 121), (66, 45), (27, 52), (52, 85), (85, 71), (71, 107), (107, 70), (70, 87), (87, 78), (78, 68), (68, 62), (62, 111), (111, 101), (101, 77), (60, 64), (64, 53), (53, 135), (135, 82), (82, 83), (83, 89), (89, 90), (90, 119), (84, 142), (142, 88), (88, 91), (79, 143), (79, 94), (110, 74), (74, 67), (67, 102), (102, 95), (95, 108), (108, 113), (109, 93), (109, 114), (69, 99), (69, 140), (75, 120), (72, 115), (72, 61), (93, 148), (54, 134), (54, 137), (105, 145), (145, 80), (80, 63), (63, 127), (86, 92), (86, 147), (147, 138), (138, 126), (131, 103), (131, 81), (103, 112), (149, 133), (149, 97), (97, 55), (133, 123), (81, 144), (148, 141), (114, 136), (136, 130), (122, 98), (91, 116), (116, 128), (124, 132), (118, 51)])

# ottimo globale (costo 0)
#mst =  [(7, 98), (98, 122), (0, 67), (0, 66), (67, 102), (66, 60), (1, 77), (1, 21), (77, 80), (21, 14), (9, 134), (9, 6), (134, 54), (6, 121), (4, 144), (144, 46), (8, 117), (8, 100), (117, 13), (100, 30), (2, 10), (2, 88), (10, 74), (88, 111), (74, 64), (5, 92), (5, 94), (92, 86), (94, 15), (11, 44), (11, 112), (44, 147), (112, 48), (3, 55), (3, 130), (55, 97), (130, 136), (12, 41), (12, 101), (41, 49), (101, 59), (121, 38), (13, 39), (39, 51), (14, 23), (23, 75), (17, 47), (17, 146), (47, 29), (146, 54), (15, 127), (127, 63), (16, 84), (16, 122), (84, 142), (18, 65), (18, 105), (65, 125), (105, 145), (22, 143), (22, 139), (143, 79), (139, 35), (75, 120), (24, 124), (24, 123), (124, 132), (123, 133), (25, 99), (25, 115), (99, 69), (115, 72), (26, 137), (26, 141), (137, 62), (141, 148), (58, 70), (58, 27), (70, 87), (27, 91), (32, 120), (32, 104), (104, 106), (28, 40), (28, 90), (40, 53), (90, 89), (53, 64), (36, 81), (36, 61), (81, 131), (61, 72), (37, 113), (37, 142), (113, 108), (33, 82), (33, 83), (82, 135), (83, 89), (51, 118), (46, 57), (57, 34), (34, 43), (43, 20), (29, 138), (138, 126), (19, 126), (19, 31), (31, 49), (147, 86), (30, 52), (52, 85), (38, 140), (140, 69), (48, 93), (93, 109), (35, 148), (20, 118), (50, 56), (50, 128), (56, 119), (128, 116), (119, 60), (59, 129), (129, 68), (73, 42), (73, 103), (42, 76), (103, 131), (76, 145), (125, 96), (96, 106), (45, 110), (45, 132), (110, 79), (91, 116), (85, 71), (71, 107), (107, 135), (87, 78), (78, 68), (62, 111), (80, 63), (102, 95), (95, 108), (109, 114), (114, 136), (149, 97), (149, 133)]

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
print("Ottimizzatore: ITERATED TABU_SEARCH")
print("   TABU_SIZE:",TABU_SIZE)
print("   MAX_ITER:",MAX_ITER)
print("   MAX_ITER_NO_IMPROVEMENT:",MAX_ITER_NO_IMPROVEMENT)

start_time = tick()


# Iterative Tabu Search
# no random restart perchè soluzioni buone <<<<< soluzioni mediocri
# Tabu Search + accettazione probabilistica dei peggioramenti
best_cost = G.number_of_nodes() - 1
n_hang = 0
S_elite = []

for i in range(1,MAX_RESTART+1):
    print("[INFO] Inizio step {}/{}".format(i,MAX_RESTART))
    results = tabu_search(G, start_solution=mst, ROOT_NODE=ROOT_NODE, 
                            TABU_SIZE=TABU_SIZE, 
                            MAX_ITER_BEFORE_ASCEND=MAX_ITER_BEFORE_ASCEND,
                            MAX_ITER=MAX_ITER, MAX_ITER_NO_IMPROVEMENT=MAX_ITER_NO_IMPROVEMENT)
    mst = results["solution"]
    cost_i = cost(mst, ROOT_NODE)

    print("[INFO] Step {}/{} completato. Costo: {}".format(i,MAX_RESTART,cost_i))
    MAX_ITER_BEFORE_ASCEND += 150
    MAX_ITER_NO_IMPROVEMENT += 100

    S_elite.append({"mst": mst.copy(), "cost": cost_i})

    if cost_i < best_cost:
        cost_best = cost_i
        if cost_i == 0:
            break
    else:
        n_hang += 1
    if n_hang > 2:
        print("[INFO] Stallo raggiunto")
        break

    # Diversificazione/Intensificazione
    # tolgo un arco e lo sostituisco con 
    # un altro arco del taglio che si crea
    #
    # non posso usare robe come 
    # 2-opt o city swap perchè il grafo non è completo
    non_optimal_nodes = [(n, {"degree": x-(ROOT_NODE!=n)*1}) for (n,x) in mst.degree() if x > 2 or (n == ROOT_NODE and x > 1)] # Nodi di grado 3 + la radice se ha grado 2
    non_optimal_nodes.sort(key=lambda x : x [1]["degree"], reverse=True) # sort by max degree

    for n1 in non_optimal_nodes[0:DIVERSIFICATION_BATCH_SIZE]:
        n1 = n1[0]
        for n2 in mst.adj[n1]:
            remove_candidate = (n1,n2)
            temp = mst.copy() # necessario per evitare RuntimeError: dictionary changed size during iteration
            # Destroy 
            temp.remove_edges_from([remove_candidate]);

            # Repair
            pool = list(build_depth_first_mst(temp, remove_candidate[0]).nodes) # nodi raggiungibili da una delle estremità dell'arco rimosso
            cut = networkx.edge_boundary(G, pool) # archi del taglio creatosi eliminando remove_candidate

            best_swap = {"out": remove_candidate, "in": remove_candidate, "cost": 2*cost_i}
            for insert_candidate in [e for e in cut if e != remove_candidate]:
                temp.add_edges_from([insert_candidate])
                deltaC = best_swap["cost"] - cost(temp, ROOT_NODE)
                if deltaC > 0:
                    best_swap = {"out": remove_candidate, "in": insert_candidate, "cost": cost(temp, ROOT_NODE)}
                temp.remove_edges_from([insert_candidate])

        # Applica mossa di diversificazione
        print("[INFO] Perturbazione")
        print("       out: {} in: {}".format(best_swap["out"],best_swap["in"]))
        mst.remove_edges_from([best_swap["out"]])
        mst.add_edges_from([best_swap["in"]])
        print("[INFO] Costo: ",cost(mst,ROOT_NODE))
                    

    
    # TODO: Prove con Path Relinking
    if False and i > 1:
        S_i = S_elite.pop()
        Moves = mst.copy()
        Moves.remove_edges_from(S_i.edges)

end_time = tick()

# Prendi la soluzione migliore prodotta
mst = min(S_elite, key=lambda s : s["cost"])["mst"]


iter = results["elapsed_iterations"]
iters_since_last_improvement = results["since_last_improvement_iterations"]

# PRINT RESULTS
print("Costo finale: ", cost(mst, ROOT_NODE), "(in",(end_time-start_time),"secondi)")
print("MST = ",list(mst.edges))

print("")
print("---DETTAGLI---")
print("Costo finale: ", cost(mst, ROOT_NODE))
print("Tempo di esecuzione: ",(end_time-start_time),"secondi")
#print("Iterazioni complessive eseguite: {}/{}".format(iter,MAX_ITER))
#print("Iterazioni eseguite dall'ultimo miglioramento di funzione obiettivo: {}/{}".format(iters_since_last_improvement ,MAX_ITER_NO_IMPROVEMENT))
print("Stallo raggiunto: ", n_hang > 2)
print("Nodi non ottimali (nodo: n. figli): ",[{n: x-(ROOT_NODE!=n)*1} for (n,x) in mst.degree() if x > 2])
V = G.number_of_nodes()
E = G.number_of_edges()
print("|V| = ", V)
print("|E| = ", E)



# PROVA SALVATAGGIO
timestamp =  datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
filename = "ITERATED-HYBRID-TABU_{}_{}__cost_{}_{}.json".format(V, E, results["cost"], timestamp)
with open("solutions/"+filename, "w+") as f:
    data = save_graph(mst)
    json.dump(data,f)


# PROVA CARICAMENTO
#from networkx.readwrite import node_link_graph as load_graph

#with open("solutions/"+filename, "r") as f:
#    data = json.load(f)
#    mst1 = load_graph(data)
#    print("MST Loaded: ",list(mst1.edges))