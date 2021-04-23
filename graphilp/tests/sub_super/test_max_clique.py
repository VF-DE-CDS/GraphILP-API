# +
import networkx as nx

from graphilp.sub_super import max_clique_cover as mcc
from graphilp.sub_super import max_clique_pack as mcp

from graphilp.imports import networkx as nxi

def test_max_clique():
    # create complete graph with two edges removed
    graph_size = 10
    
    G = nx.complete_graph(graph_size)    
    G.remove_edges_from([(1,2), (4,5)])
    
    oG = nxi.read(G)
    
    # generate models
    m_cover = mcc.create_model(oG)
    m_pack = mcc.create_model(oG)
    
    # solve models
    m_cover.optimize()
    m_pack.optimize()
    
    # extract solution
    clique_from_cover = mcc.extract_solution(oG, m_cover)
    clique_from_pack = mcc.extract_solution(oG, m_pack)
    
    # check solution
    assert(len(clique_from_cover) == graph_size - 2)
    assert(len(clique_from_pack) == graph_size - 2)
