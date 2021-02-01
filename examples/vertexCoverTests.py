import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('..'))
from imports import ilpgraph, read_mis, read_edges
from imports import networkx as imp_nx
from covering import min_vertexcover as minVC
import networkx as nx
from gurobipy import *
import xlsxwriter

if __name__ == '__main__':

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, r'..\examples\MVC_testInstances\frb59-26-5.mis')
    #path = os.path.join(dirname, r'..\partitioning\test_instances\frb59-26-5.mis')
    G = read_mis.mis_to_networkx(path)
    #G = imp_nx.col_file_to_networkx(path)
    Graph = imp_nx.read(G)

    model = minVC.createModel(Graph, True)

    