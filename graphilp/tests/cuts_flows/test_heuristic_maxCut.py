# +
from networkx import Graph
from graphilp.imports import networkx as impnx
from graphilp.cuts_flows.heuristics import maxcut_greedy

G = Graph()
G.add_weighted_edges_from([(1,3,2),(3,5,1),(5,6,1),(4,6,3),(6,7,1),(4,7,1),(2,4,3),(1,2,1),(3,4,1),(1,2,1),(1,4,1)])

optG = impnx.read(G)

cut, cutsize = maxcut_greedy.get_heuristic(optG)

assert(cutsize >= 13)
