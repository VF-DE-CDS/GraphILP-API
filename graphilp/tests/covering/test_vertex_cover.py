# +
import networkx as nx

from graphilp.imports import networkx as nximp
from graphilp.covering import min_vertexcover

def test_vertex_cover():
    G = nx.petersen_graph()
    
    optG = nximp.read(G)
    
    m = min_vertexcover.create_model(optG)
    m.optimize()
    
    cover = min_vertexcover.extract_solution(optG, m)
    
    num_covered_edges = len([e for e in G.edges() if e[0] in cover or e[1] in cover])
    
    assert(len(cover) == 6)
    assert(num_covered_edges == G.number_of_edges())
