#%%

# PCST reductions on Road Maps
#This example retrieves a graph from [OpenStreetMap](https://www.openstreetmap.org) via the [osmnx](https://osmnx.readthedocs.io) package.
#Blablabla

#%% md

## Imports

#%%

import random
import networkx as nx
import numpy as np

import osmnx as ox
import pyproj
import time
import sys

from graphilp.imports import networkx as imp_nx
from graphilp.network import pcst_linear as stp
from graphilp.network import pcst as p
from graphilp.network.reductions import pcst_utilities as pu
from graphilp.network.reductions import pcst_basic_reductions as br
from graphilp.network.reductions import pcst_voronoi as vor
from graphilp.network.reductions import pcst_dualAscent as da


#%% md

## Choose reduction techniques

#%%
# Choose which reduction techniques to use
basic_reductions_active = True
voronoi_active = True
dualAscent_active = True

# Variables for time evaluation
basic_reductions_time = 0
voronoi_time = 0
dualAscent_time = 0
gurobi_with_reductions_time = 0
gurobi_without_reductions_time = 0

# Variables for adding more constraints based on reductions
term_deg2 = None
nodes_deg3 = None
fixed_terminals = None



#%% md

## Set up the graph

#%%

crs = pyproj.crs.CRS('epsg:31467')

#%%

place = 'Carlstadt, Düsseldorf, Deutschland'

# road network of suburb (converted to Gauss-Krüger 3)
G_ox = ox.project_graph(ox.graph_from_place(place, network_type='walk'), to_crs=crs)

node_list = list(G_ox.nodes())

# choose random terminals
# 92 seconds: [316776963, 4185973923, 4028758242, 1561453930, 584047465]
# 100 seconds: [51839401, 596188953, 3762705297, 51236114, 7274705869]
num_terminals = 5
terminals = [node_list[random.randint(0, len(node_list) -1)] for n in range(num_terminals)]
terminals =  [1561453944, 584046535, 4278667367, 1598737566, 281534788]
#terminals = [595793277, 1561453934, 4278832131, 3314944018, 8096912480]
path = "results/" + str(terminals) + "/"

#%%

#draw the road map
ox.plot_graph(G_ox, figsize=(14, 10),
              bgcolor='#FFF',
              node_color='b', save=True, filepath=path + "graph.png");

#%%



#%%


result_file = open(path + "result_file.txt", "w")
result_file.write("Terminals: " + str(terminals) + "\n")
print(terminals)

#Set up a root
root = terminals[0]
print("Root: ", root)
result_file.write("Root: " + str(root))

#%%

#%%


#%%

# draw road map and terminals
ox.plot_graph(G_ox, figsize=(14, 10),
    bgcolor='#FFF',
    node_color=['g' if n == root else'#ED0000' if n in terminals else '#00F' for n in node_list],
    node_size=[70 if n == root else 50 if n in terminals else 15 for n in node_list], save=True, filepath=path + "terminals.png");

#%%



#%%

# Transformation of the MultiDiGraph to a DiGraph because Networkx doesn't fully support Multigraphs.
G = nx.Graph(G_ox)
for e in G.edges():
    G.edges[e]['weight'] = G.get_edge_data(e[0], e[1])['length']


distance = pu.dNearestTerminals(G, root, terminals, num_terminals -1, duin = False)
distance = sum(distance) / (num_terminals -1)

prizes = []
# Set up the profit of the nodes (What is the profit of terminals?)
for node in G.nodes():
    if node in terminals:
        profit = np.random.normal(loc=distance, scale=distance/2)
        G.nodes[node]['prize'] = 300
        prizes.append(profit)
    else:
        G.nodes[node]['prize'] = 0
print(profit)
# Print size of graph
pu.show_graph_size(G, "Original graph: ", result_file)

#%% md
time_start = time.time()
## Solve the instance without any reductions for comparison


#%% md

## Use Reductions

#%% md

### Basic Reductions

#%%

if basic_reductions_active:
    br.basic_reductions(G, root)
    # Print size of graph
    pu.show_graph_size(G, "Basic reductions: ", result_file)

#%% md



### Voronoi

#%%

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
    pu.show_graph_size(G, "Voronoi: ", result_file)

#%% md

### Dual Ascent

#%%


if dualAscent_active:
    try:
        G, fixed_terminals = da.dual_ascent_tests(G, root)
    except KeyError:
        # If PCST fast throws a Key Error the upper bound solution is only the root note and therefore the real solution is only the root node.
        time_end = time.time()
        s = "Pcst-fast found only Root note, no Graph for the upperBound could be built. \nSolution is only the root node: " \
            + str(root) + "\nTime to compute: " + str(time_end - time_start) + ". \nObj. value reduction: " + str(
            G.nodes[root]['prize']) + ".\n"
        result_file.write(s + "\n")
        sys.exit(0)
    pu.show_graph_size(G, "Dual Ascent: ", result_file)

#%% md

## Plot graph after reduction

#%%

terminals = [t for t in G.nodes() if G.nodes[t]['prize'] > 0]
node_list_after_reduction = list(G.nodes())

edge_colors = ["black" if (u, v) == (584047447, 1561453932) else '#ED0000' if (u, v) in G.edges() or (v, u) in G.edges() else '#AAA' for u, v in G_ox.edges()]
edge_widths = [3 if (u, v) in G.edges() else 1 for u, v in G_ox.edges()]

ox.plot_graph(G_ox, figsize=(14, 10),
              bgcolor='#FFF',
              node_color=['red' if n == root else '#ED0000' if n in terminals else "blue" if n in node_list_after_reduction else'white' for n in
                          node_list],
              node_size=[80 if n == root else 60 if n in terminals else 15 for n in node_list],
              edge_color=edge_colors, edge_linewidth=edge_widths, save=True, filepath=path + "after_reduction.png");

#%% md

# Use gurobi to run the optimisation problem

#%%

#solution, best_val = pu.gurobi(G, root, False, term_deg2, nodes_deg3, False, fixed_terminals)
#time_end = time.time()


G = nx.to_undirected(G)
optG = imp_nx.read(G)
m = stp.create_model(optG, forced_terminals=[root], weight='weight')
m.optimize()

#m = p.create_model(optG, forced_terminals=[root], weight='weight')
#m.optimize(p.callback_cycle)

timeout = 10 * 60
m.setParam('TimeLimit', timeout)
m.optimize()
best_val = m.objVal
solution = stp.extract_solution(optG, m)
time_end = time.time()
if m.Runtime + 1 > timeout:
    result_file.write("\nTimeout!\n")

#edge_colors = ['#ED0000' if (u,v) in solution or (v, u) in solution else '#AAA' for u, v in G.edges()]
#edge_widths = [3 if (u,v) in solution else 1 for u, v in G.edges()]


#%% md

## Plot the solution

#%%

node_list1 = [u for (u, v) in solution]
node_list2 = [v for (u, v) in solution]
res_node_list = list(set(node_list1 + node_list2))
res_terminals = [t for t in res_node_list if t in terminals]


edge_colors = ['#ED0000' if (u, v) in solution or (v, u) in solution else '#AAA' for u, v in G_ox.edges()]
edge_widths = [3 if (u, v) in solution else 1 for u, v in G_ox.edges()]

ox.plot_graph(G_ox, figsize=(14, 10),
              bgcolor='#FFF',
              node_color=['red' if n == root else '#ED0000' if n in res_terminals else "blue" if n in res_node_list else 'white' for n in node_list],
              node_size=[80 if n == root else 60 if n in res_terminals else 15 for n in node_list],
              edge_color=edge_colors, edge_linewidth=edge_widths, save=True, filepath=path + "solution_with_reductions.png");


#%% md

## Compare times used

#%%

s = "\nTime to compute: " + str(time_end - time_start) + ". \n"
s += "Obj. value reduction: " + str(best_val) + ". \n\n"
result_file.write(s)
print(s)
result_file.close()