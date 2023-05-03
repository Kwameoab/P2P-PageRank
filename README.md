# P2P-PageRank
An implementation of various PageRank solvers and the algorithm for calculating PageRank in a distributed, P2P system as presented by Sankaralingam et al.

## To run PageRank solvers
Use the help function to see the available options. First run:
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
To generate a testing script, run 
```
python generate_testing.py
```
Make sure you've also generated the graph beforehand. Use the help function to see the available options.
Then run:
```
sudo mn --topo=single,5
```
Then, inside mininet, run
```
source testing.sh
```