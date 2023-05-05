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

## (In-progress) To run Mininet simulation of Distributed Pagerank Algorithm (with keyword search)
First, we create the graph:
```
python3 createGraph.py -n 10789 -f graph_ks.json -s 50
```
Next, we generate our document corpus and other details:
```
cd corpus
python3 generate_corpus.py -gi ../graph_ks.json -t 60
cd .. 
```
To generate a testing script, run 
```
python3 generate_testing.py -t testing_ks.sh -r P2P_ks_results -f corpus/graph_ks_docs.json -s 50
```
Make sure you've also generated the graph beforehand. Use the help function to see the available options.
Then run:
```
sudo mn --topo=single,50
```
Then, inside mininet, run
```
source testing_ks.sh
```
