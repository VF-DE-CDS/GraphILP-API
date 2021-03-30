# +
from networkx import complete_bipartite_graph
from graphilp.imports import networkx as nximp
from graphilp.network import Steiner_Linear_with_Flow as slf

G = complete_bipartite_graph(16, 8)
terminals = [0,1,14,15]
root = 2

for n in G.nodes():
    G.nodes[n]['Weight'] = 1

G.nodes[root]['Weight'] = 10 

for t in terminals:
    G.nodes[t]['Weight'] = 10
    
for e in G.edges():
    G.edges[e]['Capacity'] = 32
    
optG = nximp.read(G)

m = slf.createModel(optG, terminals, root)
m.optimize()

result = slf.extractSolution(optG, m)
assert(len(result) == 4)
