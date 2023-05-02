# P2P-PageRank
An implementation of various PageRank solvers and the algorithm for calculating PageRank in a distributed, P2P system as presented by Sankaralingam et al.

## To run PageRank solvers
First run:
```
python createGraph.py
```
Then, create a results folder, and run:
```
python -m solvers.PageRankSolver
```
```
python -m solvers.randomWalkerSolver
```
```
python -m solvers.simpleSolver
```
```
python -m solvers.matrixSolver
```

## To run Mininet simulation of Distributed Pagerank Algorithm
TBD
