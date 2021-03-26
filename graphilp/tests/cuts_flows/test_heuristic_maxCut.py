# +
import numpy as np
import networkx as nx
import scipy.sparse as sp
from graphilp.imports import ilpsetsystem as ilpss
from graphilp.imports import readFile
from graphilp.cuts_flows.heuristics import maxcut_greedy

G = nx.Graph()
G2 = nx.Graph()
G2.add_weighted_edges_from([(1,3,2),(3,5,1),(5,6,1),(4,6,3),(6,7,1),(4,7,1),(2,4,3),(1,2,1),(3,4,1),(1,2,1),(1,4,1)])

sol = maxcut_greedy.getHeuristic(G2)

assert(sol == 13)
# -




