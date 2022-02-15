# #59. Constrained MST
A Tabu Search application to the children-constrained constrained MST problem

This project was made as a part of the Operational Reaserch exam from my master's degree program at the University of Ferrara.

### Description
Given an undirected, non-complete graph, and given a node r, find the root r spanning tree that minimizes the number of children of each node -1.  
In other words, given a spanning tree, oriented from the root, each nonleaf node i has ki ≥ 1 children. We want to minimize the sum over all i nonleaf nodes by ki-1.

### Benchmarks

> TODO: re-run

| #Nodes | #Edges | Best cost (Local Search) | CPU Time (Local Search) | Best cost (Tabu Search) | Best cost (Tabu Search) |
|-----|-----|-----|-----|-----|-----|
| 8 | 24 | 1 | 0.1s | 0 | 0.1s |
| 16 | 116 | 3 | 0.3s | 0 | 0.3s |
| 26 | 321 | 5 | 1m59s | 0 | 2.3s |
| 49 | 1172 | 12 | 10.6s | 0 | 18.2s |
| 86 | 3651 | 21 | 6m53s | 0 | 2m19s |
| 106 | 5561 | 23 | 5m22s | 0 | 4m54s |
| 126 | 7871 | 32 | 3m36s | 0 | 9m16s |

