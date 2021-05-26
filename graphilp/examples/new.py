#%%

# PCST reductions on Road Maps
#This example retrieves a graph from [OpenStreetMap](https://www.openstreetmap.org) via the [osmnx](https://osmnx.readthedocs.io) package.
#Blablabla

#%% md

## Imports

#%%

import random
import networkx as nx
from gurobipy import Model, GRB, quicksum
import numpy as np

import osmnx as ox
import pyproj
import time
import sys

from graphilp.imports import networkx as imp_nx
from graphilp.imports import readFile as gf
from graphilp.network import pcst_linear as stp
from graphilp.network import pcst as p
from graphilp.network.reductions import pcst_utilities as pu
from graphilp.network.reductions import pcst_basic_reductions as br
from graphilp.network.reductions import pcst_voronoi as vor
from graphilp.network.reductions import pcst_dualAscent as da
from graphilp.network.heuristics import steiner_metric_closure as smc

from graphilp.network import pcst_linear_tightened as plt


# Choose which reduction techniques to use
basic_reductions_active = True
voronoi_active = True
dual_ascent_active = True


# Variables for adding more constraints based on reductions
term_deg2 = None
nodes_deg3 = None
fixed_terminals = None

cologne = True
pucnu = False
vodafone = False

to_rooted = False
ilp_method = "pcst"
timeout = 310
gap = 0.0


forced_terminals = []
if cologne == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance/data/Dimacs/RPCST-cologne/cologne1/i101M2.stp"
    result_file = open("/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance/data/res.txt", "w")
    result_file.write("Instance: " + stp_file[35:41] + "\n")
    G, terminals, root = gf.stp_rooted_to_networkx(stp_file)
    # TODO: Ändere Ergebnis um 1
    forced_terminals = []

if pucnu == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance_rooted/data/Dimacs/PCSPG-PUCNU/bip42nu.stp"
    G, terminals = gf.stp_to_networkx(stp_file)
    root = -1

if vodafone == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance/data/vodafone/dap_graph_37488.stp"
    G, terminals = gf.stp_to_networkx(stp_file)
    root = -1

sum_of_prizes = 0
for n in G.nodes():
    sum_of_prizes += G.nodes[n]['prize']

if to_rooted == True:
    G, forced_terminals, sum_of_profits, root = pu.pcst_to_rpcst(G)
    for t in forced_terminals:
        G.nodes[t]['prize'] = float("inf")

pu.show_graph_size(G, "Original graph: ", None)
time_start = time.time()



if basic_reductions_active:
    br.basic_reductions(G, root)
    # Print size of graph
    pu.show_graph_size(G, "Basic reductions: ", None)


if voronoi_active:
    try:
        term_deg2, nodes_deg3 = vor.reductionTechniques(G, root)
    except KeyError:
        # If PCST fast throws a Key Error the upper bound solution is only the root note and therefore the real solution is only the root node.
        time_end = time.time()
        s = "Pcst-fast found only Root note, no Graph for the upperBound could be built. \nSolution is only the root node: " \
            + str(root) + "\nTime to compute: " + str(time_end - time_start) + ". \nObj. value reduction: " + str(
            G.nodes[root]['prize']) + ".\n"
        result_file.write(s + "\n")
        print(s)
        sys.exit(0)
    except ValueError:
        print("Instance already reduced to the root")
    pu.show_graph_size(G, "Voronoi: ", None)



if dual_ascent_active:
    try:
        G, fixed_terminals = da.dual_ascent_tests(G, root)
    except KeyError:
        # If PCST fast throws a Key Error the upper bound solution is only the root note and therefore the real solution is only the root node.
        time_end = time.time()
        s = "Pcst-fast found only Root note, no Graph for the upperBound could be built. \nSolution is only the root node: " \
            + str(root) + "\nTime to compute: " + str(time_end - time_start) + ". \nObj. value reduction: " + str(
            G.nodes[root]['prize']) + ".\n"
        print(s)
        sys.exit(0)
    except ValueError:
        print("Instance already reduced to the root")
    pu.show_graph_size(G, "Dual Ascent: ", None)

if to_rooted:
    for t in forced_terminals:
        G.nodes[t]['prize'] = 0

terminals = pu.computeTerminals(G)
G = nx.to_undirected(G)
optG = imp_nx.read(G)
warmstart, lower_bound = smc.get_heuristic(optG, terminals)
#warmstart = []
#lower_bound = None

if ilp_method == "pcst":
    m = p.create_model(optG, forced_terminals=forced_terminals, weight='weight', warmstart = warmstart, lower_bound = lower_bound)
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize(p.callback_cycle)
elif ilp_method == "pcst_linear":
    m = stp.create_model(optG, forced_terminals=forced_terminals, weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif ilp_method == "pcst_linear_tightened":
    m = plt.create_model(optG, forced_terminals=forced_terminals, weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
best_val = m.objVal
solution = p.extract_solution(optG, m)
time_end = time.time()



result = sum_of_prizes
res_nodes = set()
for (u, v) in solution:
    result += G.get_edge_data(u, v)['weight']
    res_nodes.add(u)
    res_nodes.add(v)
for u in G.nodes():
    if u in res_nodes:
        result -= G.nodes[u]['prize']
if to_rooted:
    result -= len(forced_terminals) * sum_of_profits


print(result)
print("Gurobi gap is:", m.MIPGap, "%")
print(solution)
