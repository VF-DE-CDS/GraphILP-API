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
from graphilp.network.transformations import pcst_to_sap as pts
from graphilp.network.reductions import pcst_utilities as pu
from graphilp.network.reductions import pcst_basic_reductions as br
from graphilp.network.reductions import pcst_voronoi as vor
from graphilp.network.reductions import pcst_dualAscent as da
from graphilp.network.heuristics import steiner_metric_closure as smc

from graphilp.network import pcst_linear_tightened as plt
from graphilp.network import pcst_flow_thomas as pft
from graphilp.network import pcst_flow as pf
from graphilp.network import pcst_flow_v2 as pf2
from graphilp.network import pcst_flow_indicator as pfi
from graphilp.network import pcst_morris as pm



# Choose which reduction techniques to use
basic_reductions_active = False
voronoi_active = False
dual_ascent_active = False


# Variables for adding more constraints based on reductions
term_deg2 = None
nodes_deg3 = None
fixed_terminals = None

cologne = True
pucnu = False
vodafone = False
minimal = False

to_rooted = False
warmstart_used = False
ilp_method = ["morris"]
lower_bound = None
warmstart = None
timeout = 50
gap = 0.0


forced_terminals = []
if cologne == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance/data/Dimacs/RPCST-cologne/cologne1/i101M2.stp"
    G, terminals, root = gf.stp_rooted_to_networkx(stp_file)
    forced_terminals = [root]
    #G.nodes[root]['prize'] = 1


if pucnu == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance_rooted/data/Dimacs/PCSPG-PUCNU/bip42nu.stp"
    G, terminals = gf.stp_to_networkx(stp_file)
    root = -1

if vodafone == True:
    stp_file = "/home/addimator/Dropbox/WiSe21/Projektarbeit/real_instance/data/vodafone/dap_graph_37488.stp"
    G, terminals = gf.stp_to_networkx(stp_file)
    root = -1

if minimal == True:
    G = nx.Graph()
    G.add_nodes_from([
        (1, {'prize': 6}),
        (2, {'prize': 0}),
        (3, {'prize': 4}),
        (4, {'prize': 9})

    ])

    G.add_edges_from([(1, 2, {'weight': 1}), (1, 3, {'weight': 4}), (2, 3, {'weight': 1})
                      ])
    roots = []
    terminals = [1, 4, 7, 9]
    root = -1

sum_of_prizes = 0
for n in G.nodes():
    sum_of_prizes += G.nodes[n]['prize']

if to_rooted == True:
    G, forced_terminals, sum_of_profits, root = pu.pcst_to_rpcst(G)
    for t in forced_terminals:
        G.nodes[t]['prize'] = float("inf")

term_orig = terminals.copy()
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


G = nx.to_undirected(G)
optG = imp_nx.read(G)
warmstart = []
if warmstart_used:
    terminals = pu.computeTerminals(G)
    warmstart, lower_bound = smc.get_heuristic(optG, terminals)

if "pcst" in ilp_method:
    m = p.create_model(optG, forced_terminals=[], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize(p.callback_cycle)
if "pcst_linear" in ilp_method:
    m = stp.create_model(optG, forced_terminals=[root], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "pcst_linear_tightened" in ilp_method:
    m = plt.create_model(optG, forced_terminals=[root], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "pcst_flow" in ilp_method:
    m = pf.create_model(optG, forced_terminals=[root], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "pcst_flow2" in ilp_method:
    m = pf2.create_model(optG, forced_terminals=[root], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "pcst_flow_indicator" in ilp_method:
    m = pfi.create_model(optG, forced_terminals=[root], weight='weight', use_experimental=True)
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "pcst_flow_thomas" in ilp_method:
    m = pft.create_model(optG, forced_terminals=[], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize()
elif "morris" in ilp_method:
    G_sa, art_root = pts.steiner_arborescence_transformation(G, forced_terminals = [root])
    optG_sa = imp_nx.read(G_sa)
    m = pm.create_model(optG_sa, art_root, forced_terminals=[root], weight='weight')
    m.setParam('TimeLimit', timeout)
    m.setParam('MIPGap', gap)
    m.optimize(pm.callback_connect_constr)
    solution = pm.extract_solution(optG_sa, m)
    print(solution)
    solution = [(u, v) for (u, v) in solution if u != max(G.nodes()) + 1 and v != max(G.nodes()) + 1 ]
    result = m.objVal


best_val = m.objVal
#solution = p.extract_solution(optG, m)
time_end = time.time()


#result = pu.computeMinimizationResult(sum_of_prizes, G, solution)


if to_rooted:
    result -= len(forced_terminals) * sum_of_profits

print("\nObjective value:", result)
print("Solution:", solution)
print("Time to compute: ", str(time_end - time_start) + ".")
print("Gurobi gap is:", m.MIPGap, "%")
pu.validate_solution(solution, G, term_orig, result)
