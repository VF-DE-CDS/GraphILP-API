# +
import networkx as nx
import graphilp
from graphilp.imports import networkx as imp_nx
from graphilp.network.heuristics import tsp_nearest_neighbour as NN
from graphilp.network.heuristics import tsp_two_opt as twoOpt
from gurobipy import *
import xlsxwriter
import random
import matplotlib.pyplot as plt
import tsplib95

# Path of the TSPLib Instance
path = path = graphilp.__path__[0] + r"/examples/TSPTestInstances/kroB150.tsp"

# Loading problem via tsplib95. Returns a dictionary with a bunch of information.
problem = tsplib95.load(path)

#Transform the problem to a graph
G = problem.get_graph()

# Transform the Graph to an ilpGraph
Graph = imp_nx.read(G)

# Calculate Nearest Neighbours
tour, length = NN.getHeuristic(Graph)
assert(length == 34499)

# Improve with 2 OPT Heuristic
tour, length = twoOpt.getHeuristic(Graph, tour, length)

assert(length == 26508)
# -


