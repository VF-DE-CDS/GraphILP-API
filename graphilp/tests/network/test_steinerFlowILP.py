# +
from graphilp.imports import ilpgraph, readFile
from graphilp.imports import networkx as imp_nx
from graphilp.network import Steiner_Linear_with_Flow as sflow
import graphilp
import networkx as nx
from gurobipy import *
import xlsxwriter
import random
import matplotlib.pyplot as plt

path = graphilp.__path__[0] + "/examples/Steiner_testInstances/e10.stp"
G, terminals = readFile.stp_to_networkx(path)

for edge in G.edges():
    G[edge[0]][edge[1]]['Cost'] = 1
    
root = 2411

assert(nx.is_connected(G))
assert(root in terminals)

Graph = imp_nx.read(G)

for node in G.nodes(data=True):
    if node in terminals:
        node[1]['Weight'] = 1
    else:
        node[1]['Weight'] = 0
    
    
    
model = sflow.createModel(Graph, terminals, 'weight', root)
model.optimize()
print(model.objVal)
# -


