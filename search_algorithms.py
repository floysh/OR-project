import os
import networkx as nx

from shared import *


# debug settings
if not "DEBUG_IMPROVEMENT" in globals():
    DEBUG_IMPROVEMENT = False

if not "SAVE_STEP_GRAPHS" in globals():
    SAVE_STEP_GRAPHS = False


# search parameters
MAX_ITER = 1000
MAX_ITER_SAME_COST = 500



def local_search(G, start_solution, ROOT_NODE, MAX_ITER):
    # compatibilità vecchio codice
    mst = start_solution 

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
    while iter < MAX_ITER and iters_since_last_improvement < MAX_ITER_SAME_COST:
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


def tabu_search(G, start_solution, ROOT_NODE, TABU_SIZE=10, MAX_ITER=MAX_ITER, MAX_ITER_SAME_COST=MAX_ITER_SAME_COST):
    # compatibilità vecchio codice
    mst = start_solution

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
    while iter < MAX_ITER and iters_since_last_improvement < MAX_ITER_SAME_COST:
        iter += 1
        
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
        for e in [x for x in loop_edges if (x != new_e)]:
            temp = mst.copy()
            temp.remove_edges_from([e])
            
            cost_after = cost(temp, root_node=ROOT_NODE)

            # Penalizza le mosse proibite!
            if e in tabu_list:
                cost_after += G.number_of_nodes()
            
            step = (cost_after, e)
            Moves.append(step)

            # Smetti di esplorare appena trovi una mossa migliorativa
            # OK perchè scambiando archi il massimo decremento di costo è 1
            # per ogni iterazione
            if cost_after < cost_before:
                move_k = step
                break
            
        # Se non hai trovato mosse che migliorano la soluzione
        # prendi la meno peggio
        if move_k == None:
            Moves.sort()
            move_k = Moves.pop(0) # ordina in base al costo e prende la prima mossa
        cost_k = move_k[0]
        out_e = move_k[1]
        
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

            # L'arco che non entra in soluzione deve tornare
            # nel grafo complementare
            out_candidates.append(out_e)

            iters_since_last_improvement = 0
        else:
            iters_since_last_improvement += 1

            if cost_k <= cost_before: #and (out_e not in tabu_list):
                # La mossa migliore non è proibita (non esploro mosse proibite)
                # ma non abbassa il costo della soluzione.
                # Continuo a esplorare
                # 
                if len(tabu_list) == TABU_SIZE:
                    e = tabu_list.pop(0)
                    out_candidates.append(e)
                tabu_list.append(new_e) # è proibito rimuovere il nuovo arco

                tabu_list.pop(0)


                out_candidates.append(out_e)
            else:
                # Sto peggiorando o facendo cose proibite che non vanno bene,
                # annulla tutto
                mst.remove_edges_from([new_e])
                mst.add_edges_from([out_e])

                out_candidates.append(new_e) # lo metto in fondo per provare a fare altri scambi prima di ripescarlo


    return {
        "solution": S_best,
        "cost": cost(S_best, root_node=ROOT_NODE),
        "elapsed_iterations": iter,
        "since_last_improvement_iterations": iters_since_last_improvement
    }
