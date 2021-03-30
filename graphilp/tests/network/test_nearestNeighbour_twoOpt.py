# +
from networkx import complete_graph
from graphilp.network.heuristics import tsp_nearest_neighbour as NN
from graphilp.network.heuristics import tsp_two_opt as twoOpt
from graphilp.imports import networkx as imp_nx

graph_size = 100
G = complete_graph(graph_size)

# Transform the Graph to an ILPGraph
Graph = imp_nx.read(G)

# Calculate Nearest Neighbours
tour, length = NN.get_heuristic(Graph)
assert(len(tour) == graph_size)

# Improve with 2 OPT Heuristic
tour, length = twoOpt.get_heuristic(Graph, tour, length)

assert(len(tour) == graph_size)
