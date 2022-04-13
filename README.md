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

| #Nodes | #Edges | Best cost (Greedy) | CPU Time (Greedy) | Best cost (LS) | CPU Time (LS) | Best cost (Tabu Search) | CPU Time (Tabu Search) |
|--------|--------|-----|--------|-----|--------|-----|--------|
|      8 |     28 |   0 |   0.2s |   1 |   0.1s |   0 |   0.1s | 
|     16 |    148 |   0 |   0.3s |   2 |   0.6s |   0 |   0.6s |
|     26 |    325 |   0 |   0.9s |   4 |   2.8s |   0 |   1.8s |
|     49 |   1176 |   0 |   0.7s |  13 |  26.2s |   0 |  16.5s |
|     86 |   3655 |   0 |   0.2s |  18 |  6m52s |   0 |   2m8s |
|    106 |   5565 |   0 |   0.2s |  24 |  8m09s |   0 |  4m44s |
|    126 |   7875 |   0 |   0.3s |  32 |  9m46s |   0 |  9m40s |
|    226 |  25425 |   0 |   0.2s | --- |  ----- |   0 | 96m54s |
<!-- N        E    BestGr TimeGr  BestLS TimeLS BestTabu TimeTabu-->


**Generator: SPARSE**

> random seed: 191295  
> root node: 7

| #Nodes | #Edges | Best cost (Greedy) | CPU Time (Greedy) | Best cost (LS) | CPU Time (LS) | Best cost (Tabu Search) | CPU Time (Tabu Search) |
|--------|--------|-----|--------|-----|--------|-----|--------|
|      8 |        |     |        |     |        |     |        |
|     16 |        |     |        |     |        |     |        |
|     26 |        |     |        |     |        |     |        |
|     49 |        |     |        |     |        |     |        |
|     86 |        |     |        |     |        |     |        |
|    106 |        |     |        |     |        |     |        |
|    126 |        |     |        |     |        |     |        |
|    226 |    669 |  74 |   0.2s | --- |  ----- |  19 | 32m17s |



**Generator: NOT_BEST_PATH**

> random seed: 191295  
> root node: 5

| #Nodes | #Edges | Best cost (Greedy) | CPU Time (Greedy) | Best cost (LS) | CPU Time (LS) | Best cost (Tabu Search) | CPU Time (Tabu Search) |
|--------|--------|-----|--------|-----|--------|-----|--------|
|      8 |    --- | --- |   ---- | --- |  ----- | --- |  ----- | 
|     16 |     20 |   9 |   0.1s |     |        |   9 |  11.3s |
|     26 |     55 |  10 |   0.2s |     |        |   9 |  29.5s |
|     49 |    133 |  22 |   0.2s |     |        |  19 |  57.1s |
|     86 |    265 |  39 |   0.1s |     |        |  33 |  2m29s |
|    106 |    335 |  52 |   0.3s |     |        |  41 |  3m32s |
|    126 |    405 |  61 |   0.1s |     |        |  49 |  4m30s |
|    226 |    775 | 112 |   0.2s |     |        |  89 | 11m51s |