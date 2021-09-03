# +
import networkx as nx

from graphilp.imports import networkx as nx_imp
from graphilp.matching import perfect_bipartite as bm

def test_perfect_bipartite():
    # create graph instance
    G = nx.complete_bipartite_graph(4, 4)
    G.add_weighted_edges_from([(0, 6, 2), (1, 4, 2), (2, 5, 2), (3, 7, 2)])
    
    optG = nx_imp.read(G)
    
    # generate model
    m = bm.create_model(optG, range(4))
    
    # solve model
    m.optimize()
    
    # extract solution
    matching = bm.extract_solution(optG, m)
    
    # check solution
    assert(len(matching) == 4)
    assert(m.objVal == 8)
