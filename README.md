# #59. Constrained MST
A Tabu Search application to the children-constrained constrained MST problem

This project was made as a part of the Operational Reaserch exam from my master's degree program at the University of Ferrara.

### Description
Given an undirected, non-complete graph, and given a node r, find the root r spanning tree that minimizes the number of children of each node -1.  
In other words, given a spanning tree, oriented from the root, each nonleaf node i has ki ≥ 1 children. We want to minimize the sum over all i nonleaf nodes by ki-1.

### Benchmark

**Generator: NX_DENSE**

> random seed: 191295  
> root node: 7

| #Nodes | #Edges | Best cost (Local Search) | CPU Time (Local Search) | Best cost (Tabu Search) | CPU Time (Tabu Search) |
|--------|--------|-----|-----|-----|-----|
| 8 | 28 | 1 | 0.1s | 0 | 0.1s | 
| 16 | 148 | 2 | 0.6s | 0 | 0.6s |
| 26 | 325 | 4 | 2.8s | 0 | 1.8s |
| 49 | 1176 | 13 | 26.2s | 0 | 16.5s |
| 86 | 3655 | 18 | 6m52s | 0 | 2m8s |
| 106 | 5565 | 24 | 8m9s | 0 | 4m44s |
| 126 | 7875 | 32 | 9m46s | 0 | 9m40s |
| 226 | 7875 | N.A | N.A | 0 | 96m54s |
