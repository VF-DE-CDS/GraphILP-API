from graphilp.imports.readFile import stp_to_networkx
import networkx as nx
from graphilp.network.reductions import pcst_utilities as pu
import graphilp.network.pcst_linear as pl
import graphilp.imports.networkx as n
from gurobipy import Model, GRB, quicksum
import gurobipy


G, terminals, root = stp_to_networkx(
    "/home/addimator/Dropbox/WiSe21/Projektarbeit/cooperation-vodafone-data/Dimacs/RPCST-cologne/cologne1/i105M3.stp")
pu.gurobi(G, root)
print("###############################################################\n##############################################################")
G = n.read(G)
m = pl.create_model(G, forced_terminals=[root])
m.optimize()