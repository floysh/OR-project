# #59. Constrained MST
A Tabu Search application to the degree constrained MST problem.

This project was made as a part of the Operational Reaserch exam during my master's degree at the University of Ferrara.

### Description
Given an undirected, non-complete graph, and given a node $r$, find the root $r$ spanning tree that minimizes the number of children of each node -1.  
In other words, given a spanning tree, oriented from the root, each nonleaf node i has $k_i ≥ 1$ children. We want to minimize the sum over all nonleaf nodes by $ki-1$.

