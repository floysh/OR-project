from cmath import exp
import os
import random
import networkx as nx

from shared import *


# debug settings
if not "DEBUG_IMPROVEMENT" in globals():
    DEBUG_IMPROVEMENT = False

if not "SAVE_STEP_GRAPHS" in globals():
    SAVE_STEP_GRAPHS = False


# default search parameters
MAX_ITER = 1000
MAX_ITER_NO_IMPROVEMENT = 500

# Creazione di MST con radice specificata tramite visita in profondità
def greedy_depth_first(G, ROOT_NODE):
    MST = nx.Graph()
    return __recursive_depth_first(G, ROOT_NODE, MST)

def __recursive_depth_first(graph, node, MST):
    # MST è una risorsa condivisa tra le ricorsioni
    # TODO: trovare un modo più elegante di aggiornarlo
    children = graph.adj[node]
    for child in children:
        if child not in MST.nodes:
            MST.add_edge(node, child)
            MST = __recursive_depth_first(graph, child, MST)

    return MST


def local_search(G, start_solution, ROOT_NODE, **kwargs):
    # compatibilità vecchio codice
    mst = start_solution 
    MAX_ITER = kwargs.get("MAX_ITER", 3000);

    # calcolo il grafo complementare all'MST
    outer_G = G.copy()
    outer_G.remove_edges_from(mst.edges)
    #draw_graph(outer_G, root_node=ROOT_NODE)

    # Sostituti candidati = archi che possono sostituire quelli in soluzione
    # Uso questa lista per non dover ricalcolare outer_G a ogni iterazione
    out_candidates = list(outer_G.edges)

    global iter; iter = 0

    if DEBUG_IMPROVEMENT:
        print("NON IN MST:", outer_G.edges)
        print("MST:", mst.edges)

        plt.figure(0)
        plt.title("Initial")
        draw_graph(G, mst, root_node=ROOT_NODE)
        if "SAVE_STEP_GRAPHS" in globals() and SAVE_STEP_GRAPHS:
            plt.savefig( os.path.join(OUT_DIR, "debug_Steps",'iter_{}'.format(iter)) )

    global iters_since_last_improvement
    iters_since_last_improvement = 0
    force_stop = False
    while iter < MAX_ITER and iters_since_last_improvement < MAX_ITER_NO_IMPROVEMENT:
        iter += 1

        #print("[DEBUG] out candidates: ",out_candidates)
        
        new_e = out_candidates.pop(0)
        # Assicurati che l'arco estratto non sia stato (re)inserito 
        # nell'MST dopo la sua rimozione da un'altra mossa
        # (questa cosa serve solo perchè non ricreo il grafo complementare a ogni iterazione)        
        while new_e in mst.edges:
            if len(out_candidates) == 0:
                print("[WARN] Nessun sostituto candidato disponibile!")
                return mst
                force_stop = True
                break
            new_e = out_candidates.pop(0)

        cost_before = cost(mst, ROOT_NODE)

        # Se sono così fortunato da aver trovato la soluzione ottima,
        # ferma tutto (non si può mai migliorare più di così)
        if cost_before == 0:
            break
        if DEBUG_IMPROVEMENT:
            print("")
            print(iter,") initial cost: ",cost_before)
            print("MST=", list(mst.edges))
            print("add: ",new_e)

        mst.add_edges_from([new_e])

        # loop detection
        try:
            loop_edges = nx.algorithms.cycles.find_cycle(mst)
        except:
            print("[ERR]","iter=",iter, "add:{} non ha creato un ciclo".format(new_e))



        # Esplorazione intorno
        move_k = None
        for e in [x for x in loop_edges if (x != new_e)]:
            temp = mst.copy()
            temp.remove_edges_from([e])
            
            cost_after = cost(temp, ROOT_NODE)
            
            step = (cost_after, e)

            # Smetti di esplorare appena trovi una mossa migliorativa
            # OK perchè scambiando archi il massimo decremento di costo è 1
            # per ogni iterazione
            if cost_after < cost_before:
                move_k = step
                break
            
        # Se hai trovato una mossa migliorativa, applicala
        if move_k != None:
            # estraggo parametri
            cost_after = move_k[0]
            out_e = move_k[1]
            
            # applico la mossa
            mst.add_edges_from([new_e])
            mst.remove_edges_from([out_e])

            out_candidates.append(out_e)

            print("[INFO] S_{} cost={}".format(iter,cost_after))

            if DEBUG_IMPROVEMENT:
                fig = plt.figure(iter)
                plt.title("add: {}, remove: {}".format(new_e, out_e))
                draw_graph(G, mst, root_node=ROOT_NODE )
                if "SAVE_STEP_GRAPHS" in globals() and SAVE_STEP_GRAPHS:
                    plt.savefig(os.path.join(OUT_DIR,"debug_Steps",'iter_{}'.format(iter)))
                print("remove: ", out_e)

            iters_since_last_improvement = 0

        else:
            iters_since_last_improvement += 1
            # Se non hai trovato mosse che migliorano la soluzione
            # passa oltre e prova un'altra sostituzione

            if DEBUG_IMPROVEMENT:
                print("out: ",new_e,"(revert)")

            # annulla modifiche!
            mst.remove_edges_from([new_e])
            
            # Non considerare più l'arco che hai provato a sostituire
            # (Greedy!)
            out_candidates.append(new_e)

    return {
        "solution": mst,
        "cost": cost(mst, root_node=ROOT_NODE),
        "elapsed_iterations": iter,
        "since_last_improvement_iterations": iters_since_last_improvement
    }


def tabu_search(G, start_solution, ROOT_NODE, TABU_SIZE=10, **kwargs):
    # compatibilità vecchio codice
    mst = start_solution

    MAX_ITER = kwargs.get("MAX_ITER", 3000);
    MAX_ITER_NO_IMPROVEMENT = kwargs.get("MAX_ITER_NO_IMPROVEMENT",1000);
    MAX_ITER_BEFORE_ASCEND = kwargs.get("MAX_ITER_BEFORE_ASCEND", 450);
    DIVERSIFICATION_BATCH_SIZE = kwargs.get("DIVERSIFICATION_BATCH", 15);

    # calcolo il grafo complementare all'MST
    outer_G = G.copy()
    outer_G.remove_edges_from(mst.edges)
    #draw_graph(outer_G, root_node=ROOT_NODE)

    # Sostituti candidati = archi che possono sostituire quelli in soluzione
    # Uso questa lista per non dover ricalcolare outer_G a ogni iterazione
    out_candidates = list(outer_G.edges)

    # La tabu list evita di sprecare troppe iterazioni 
    # processando sempre gli stessi archi
    tabu_list = []

    # Metto qui gli Archi cattivi che portano solo a peggioramenti 
    # (per il valore di cost() corrente)
    # così evito di ritornarci.
    # Li rimetto in out_candidates quando trovo sol. di costo inferiore
    ignore_list = []

    global iter; iter = 0

    if DEBUG_IMPROVEMENT:
        print("NON IN MST:", outer_G.edges)
        print("MST:", mst.edges)

        plt.figure(0)
        plt.title("Initial")
        draw_graph(G, mst, root_node=ROOT_NODE)
        if "SAVE_STEP_GRAPHS" in globals() and SAVE_STEP_GRAPHS:
            plt.savefig( os.path.join(OUT_DIR, "debug_Steps",'iter_{}'.format(iter)) )

    S_best = nx.Graph()
    S_best.add_edges_from(list(mst.edges))
    cost_best = cost(S_best, root_node=ROOT_NODE)

    global iters_since_last_improvement
    iters_since_last_improvement = 0
    T = 0.2*(cost_best)
    
    while iter < MAX_ITER and iters_since_last_improvement < MAX_ITER_NO_IMPROVEMENT and len(out_candidates) > 0:
        iter += 1
        
        #non_optimal_nodes = [(n, {"degree": x-(ROOT_NODE!=n)*1}) for (n,x) in mst.degree() if x > 2 or (n == ROOT_NODE and x > 1)] # Nodi di grado 3 + la radice se ha grado 2
        optimal_nodes = [(n, {"degree": x-(ROOT_NODE!=n)*1}) for (n,x) in mst.degree() if x <= 2 or (n == ROOT_NODE and x == 1)]
        
        new_e = out_candidates.pop(0)
        # Assicurati che l'arco estratto non sia stato (re)inserito 
        # nell'MST dopo la sua rimozione da un'altra mossa
        # (questa cosa serve solo perchè non ricreo il grafo complementare a ogni iterazione)
        while new_e in mst.edges:
            if len(out_candidates) == 0:
                break
            new_e = out_candidates.pop(0)

        cost_before = cost(mst, root_node=ROOT_NODE)

        # Se sono così fortunato da aver trovato la soluzione ottima,
        # ferma tutto (non si può mai migliorare più di così)
        if cost_before == 0:
            break
        if DEBUG_IMPROVEMENT:
            print("")
            print(k,") initial cost: ",cost_before)
            print("MST=", list(mst.edges))
            print("add: ",new_e)


        mst.add_edges_from([new_e])

        # loop detection
        try:
            loop_edges = nx.algorithms.cycles.find_cycle(mst)
        except:
            print("[ERR]","iter=",iter, "add:{} non ha creato un ciclo".format(new_e))



        # Esplorazione intorno
        Moves = []
        move_k = None

        for e in [(x,y) for (x,y) in loop_edges if ((x,y) != new_e)]:
            temp = mst.copy()
            temp.remove_edges_from([e])
            
            cost_after = cost(temp, root_node=ROOT_NODE)
            
            move = {"cost_after": cost_after, "in": new_e, "out": e}

            if e in tabu_list:
                # Criterio di aspirazione:
                # accetta mosse proibite (solo) se portano a soluzioni
                # migliori dell'ottimo candidato
                Moves.append(move)
                if cost_after < cost_best:
                    move_k = move
                    break
            else: 
                Moves.append(move)
                # Smetti di esplorare appena trovi una mossa migliorativa
                # OK perchè scambiando archi il massimo decremento di costo è 1
                # per ogni iterazione
                if cost_after < cost_before:
                    move_k = move
                    break

        # Se tutti gli archi del ciclo intersecano nodi ottimali, non ha senso rimuoverli?
        if len(Moves) == 0:
            ignore_list.append(new_e)
            continue
            
        # Se non hai trovato mosse che migliorano la soluzione
        # prendi la meno peggio
        if move_k == None:
            move_k = min(Moves, key = lambda x : x["cost_after"])

        cost_k = move_k["cost_after"]
        out_e = move_k["out"]
        
        # applico la mossa -> genero S_k
        mst.add_edges_from([new_e])
        mst.remove_edges_from([out_e])

        if DEBUG_IMPROVEMENT:
            fig = plt.figure(iter)
            plt.title("add: {}, remove: {}".format(new_e, out_e))
            draw_graph(mst, mst, root_node=ROOT_NODE )
            if "SAVE_STEP_GRAPHS" in globals() and SAVE_STEP_GRAPHS:
                plt.savefig(os.path.join(OUT_DIR,"debug_Steps",'iter_{}'.format(iter)))
            print("remove: ", out_e)


        if cost_k < cost_best:
            # Ho trovato una mossa migliorativa
            # la soluzione attuale è la nuova sol. migliore
            S_best = mst.copy()
            cost_best = cost_k
            print("[INFO] S_{} cost={}".format(iter,cost_k))

            # L'arco che non entra in soluzione deve tornare
            # nel grafo complementare
            out_candidates.append(out_e)

            # Rimetti gli archi "cattivi" tra i candidati
            out_candidates = out_candidates + ignore_list

            iters_since_last_improvement = 0
        else:
            iters_since_last_improvement += 1

            if out_e not in tabu_list:
                if cost_k <= cost_before:
                    # La mossa migliore non è proibita 
                    # (le mosse proibite vengono ignorate se 
                    #  non migliorano l'ottimo candidato)
                    # è un miglioramento ma non abbassa il costo della soluzione ottima.
                    #
                    # Continuo a esplorare
                    # 
                    if len(tabu_list) == TABU_SIZE:
                        e = tabu_list.pop(0)
                        out_candidates.append(e)
                    tabu_list.append(new_e) # è proibito rimuovere il nuovo arco

                    tabu_list.pop(0)


                    out_candidates.append(out_e)
                else:
                    # Sto peggiorando
                    #
                    # Non peggiorare troppo
                    # (poche mosse migliorative, se degrado molto sol. 
                    #  va a finire che non miglioro più)
                    deltaE = (cost_after-cost_best)
                    if iters_since_last_improvement > MAX_ITER_BEFORE_ASCEND and deltaE <= 3:  
                        if random.random() < 0.15:
                            #print("[INFO] S_{}, cost: {} (peggiora), last improvement: {} iters ago".format(iter,cost_after,iters_since_last_improvement))
                            
                            if len(tabu_list) == TABU_SIZE:
                                e = tabu_list.pop(0)
                                out_candidates.append(e)
                            tabu_list.append(new_e) # è proibito rimuovere il nuovo arco

                            out_candidates.append(out_e)

                            out_candidates = out_candidates + ignore_list
                    else:
                        # annulla tutto!
                        mst.remove_edges_from([new_e])
                        mst.add_edges_from([out_e])

                        # arco cattivo, non considerarlo più per un po'
                        #if len(tabu_list) == TABU_SIZE:
                        #    e = tabu_list.pop(0)
                        #    out_candidates.append(e)
                        #tabu_list.append(out_e)
                        
                        # In alternativa alla tabu list principale provo a usare
                        # questa specie di tabu list secondaria, più restrittiva,
                        # che rende proibite le mosse cattive fino a quando non si migliora la f.o
                        ignore_list.append(new_e) 



                    # Diversificazione/Intensificazione
                    # tolgo un arco e lo sostituisco con 
                    # un altro arco del taglio che si crea
                    #
                    # non posso usare robe come 
                    # 2-opt o city swap perchè il grafo non è completo
                    if iters_since_last_improvement % 20 == 0:
                        non_optimal_nodes = [(n, {"degree": x-(ROOT_NODE!=n)*1}) for (n,x) in mst.degree() if x > 2 or (n == ROOT_NODE and x > 1)] # Nodi di grado 3 + la radice se ha grado 2
                        non_optimal_nodes.sort(key=lambda x : x [1]["degree"], reverse=True) # sort by max degree

                        for n1 in non_optimal_nodes[0:DIVERSIFICATION_BATCH_SIZE]:
                            n1 = n1[0]
                            for n2 in mst.adj[n1]:
                                remove_candidate = (n1,n2)
                                
                                # non applicare l'equivalente di mosse proibite!
                                if remove_candidate in tabu_list or (n2,n1) in tabu_list:
                                    continue;

                                temp = mst.copy() # necessario per evitare RuntimeError: dictionary changed size during iteration
                                # Destroy 
                                temp.remove_edges_from([remove_candidate]);

                                # Repair
                                pool = list(build_depth_first_mst(temp, remove_candidate[0]).nodes) # nodi raggiungibili da una delle estremità dell'arco rimosso
                                cut = nx.edge_boundary(G, pool) # archi del taglio creatosi eliminando remove_candidate

                                best_swap = {"out": remove_candidate, "in": remove_candidate, "cost": 2*cost_best}
                                for insert_candidate in [e for e in cut if e != remove_candidate]:
                                    temp.add_edges_from([insert_candidate])
                                    deltaC = best_swap["cost"] - cost(temp, ROOT_NODE)
                                    if deltaC > 0:
                                        best_swap = {"out": remove_candidate, "in": insert_candidate, "cost": cost(temp, ROOT_NODE)}
                                    temp.remove_edges_from([insert_candidate])

                            # Applica mossa di diversificazione
                            #print("[INFO] Perturbazione")
                            #print("       out: {} in: {}".format(best_swap["out"],best_swap["in"]))
                            mst.remove_edges_from([best_swap["out"]])
                            mst.add_edges_from([best_swap["in"]])
                            #print("[INFO] Costo: ",cost(mst,ROOT_NODE))

                            # Aggiungi l'inverso alla tabu list
                            if len(tabu_list) == TABU_SIZE:
                                e = tabu_list.pop(0)
                                out_candidates.append(e)
                            tabu_list.append([best_swap["in"]]) # è proibito rimuovere l'arco che sostituisce remove_candidate!



    return {
        "solution": S_best,
        "cost": cost(S_best, root_node=ROOT_NODE),
        "elapsed_iterations": iter,
        "since_last_improvement_iterations": iters_since_last_improvement
    }
