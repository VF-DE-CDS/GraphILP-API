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
from graphilp.network import pcst_linear as stp
from graphilp.network import pcst as p
from graphilp.network import pcst_linear_tightened as plt

from graphilp.network.reductions import pcst_utilities as pu
from graphilp.network.reductions import pcst_basic_reductions as br
from graphilp.network.reductions import pcst_voronoi as vor
from graphilp.network.reductions import pcst_dualAscent as da

pcst_m = []
pcst_lm = []
pcst_ltm = []
#%% md

## Choose reduction techniques

#%%
# Choose which reduction techniques to use
basic_reductions_active = False
voronoi_active = False
dualAscent_active = False

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

ilp_method = 'pcst_linear_tightened'
timeout = 2000



#%% md

## Set up the graph

#%%


crs = pyproj.crs.CRS('epsg:31467')

#%%

place = 'Carlstadt, Duesseldorf, Germany'

# road network of suburb (converted to Gauss-Krüger 3)
G_ox = ox.project_graph(ox.graph_from_place(place, network_type='walk'), to_crs=crs)

node_list = list(G_ox.nodes())
for i in range(1):
    num_terminals = 5
    terminals = [node_list[random.randint(0, len(node_list) -1)] for n in range(num_terminals)]
    #terminals = [1561598420, 51839401, 253875143, 1561453968, 8096912481]

    path = "results/" + str(terminals) + "/"


    ox.plot_graph(G_ox, figsize=(14, 10),
                  bgcolor='#FFF',
                  node_color='b', save=True, filepath=path + "graph.png");


    result_file = open(path + "result_file.txt", "w")
    result_file.write("Terminals: " + str(terminals) + "\n")
    print("Terminals:", terminals)

    #Set up a root
    root = terminals[0]
    print("Root: ", root)
    result_file.write("Root: " + str(root))



    # draw road map and terminals
    ox.plot_graph(G_ox, figsize=(14, 10),
        bgcolor='#FFF',
        node_color=['g' if n == root else'#ED0000' if n in terminals else '#00F' for n in node_list],
        node_size=[70 if n == root else 50 if n in terminals else 15 for n in node_list], save=True, filepath=path + "terminals.png");



    # Transformation of the MultiDiGraph to a DiGraph because Networkx doesn't fully support Multigraphs.
    G = nx.Graph(G_ox)
    for e in G.edges():
        G.edges[e]['weight'] = G.get_edge_data(e[0], e[1])['length']

    #terminals.remove(root)
    nt = terminals.copy()
    nt.remove(root)

    distance = 0
    for t in nt:
        distance += nx.shortest_path_length(G_ox, root, t, weight='length')
    distance = distance / num_terminals + 3
    prizes = [abs(np.random.normal(loc=distance, scale=distance * 2)) for i in range(num_terminals)]
    print("Prizes: ", prizes)

    #prizes = [865.0924606814847, 140.79800720142936, 295.75580543775317, 2082.135034805612, 33.5496532545593]

    for node in G.nodes():
            G.nodes[node]['prize'] = 0
    for i in range(len(terminals)):
        G.nodes[terminals[i]]['prize'] = prizes[i]

    sum_of_prizes = 0
    for n in G.nodes():
        sum_of_prizes += G.nodes[n]['prize']
    # Print size of graph
    pu.show_graph_size(G, "Original graph: ", result_file)

    #%% md
    time_start = time.time()



    if basic_reductions_active:
        br.basic_reductions(G, root)
        # Print size of graph
        pu.show_graph_size(G, "Basic reductions: ", result_file)



    if voronoi_active:
        profit = G.nodes[root]['prize']
        #G.nodes[root]['prize'] = 1000000000000000000000000
        try:
            term_deg2, nodes_deg3 = vor.reductionTechniques(G, root)
        except KeyError:
            # If PCST fast throws a Key Error the upper bound solution is only the root note and therefore the real solution is only the root node.
            time_end = time.time()
            s = "Pcst-fast found only Root note, no Graph for the upperBound could be built. \nSolution is only the root node: " \
                + str(root) + "\nTime to compute: " + str(time_end - time_start) + ". \nObj. value reduction: " + str(
                sum_of_prizes) + ".\n"
            result_file.write(s + "\n")
            print(s)
            continue
            sys.exit(0)
        #G.nodes[root]['prize'] = profit
        pu.show_graph_size(G, "Voronoi: ", result_file)


    if dualAscent_active:
            try:
                G, fixed_terminals = da.dual_ascent_tests(G, root)
            except KeyError:
                # If PCST fast throws a Key Error the upper bound solution is only the root note and therefore the real solution is only the root node.
                time_end = time.time()
                s = "Pcst-fast found only Root note, no Graph for the upperBound could be built. \nSolution is only the root node: " \
                    + str(root) + "\nTime to compute: " + str(time_end - time_start) + ". \nObj. value reduction: " + str(
                   sum_of_prizes) + ".\n"
                result_file.write(s + "\n")
                continue
                sys.exit(0)

            pu.show_graph_size(G, "Dual Ascent: ", result_file)

    translated = []
    for (u, v) in G.edges:
        try:
            translated.append(G.nodes[u]['origin'])
        except:
            pass
        try:
            translated.append(G.nodes[v]['origin'])
        except:
            pass

        if (u, v) not in G_ox.edges():
            translated += G.edges[(u, v)]['path']
        else:
            translated.append((u, v))

    node_list1 = [u for (u, v) in translated]
    node_list2 = [v for (u, v) in translated]
    res_node_list = list(set(node_list1 + node_list2))
    res_terminals = [t for t in res_node_list if t in terminals]
    print(res_terminals)

    edge_colors = ['#ED0000' if (u, v) in translated or (v, u) in G.edges else '#AAA' for u, v in G_ox.edges()]
    edge_widths = [3 if (u, v) in translated else 1 for u, v in G_ox.edges()]

    ox.plot_graph(G_ox, figsize=(14, 10),
                  bgcolor='#FFF',
                  node_color=[
                      'green' if n == root and n in res_terminals else '#ED0000' if n in res_terminals else "blue" if n in res_node_list else 'white'
                      for n in node_list],
                  node_size=[80 if n == root and n in res_terminals else 60 if n in res_terminals else 15 for n in node_list],
                  edge_color=edge_colors, edge_linewidth=edge_widths, save=True,
                  filepath=path + "solution_with_reductions.png");
    #%% md

    ilp_method = "pcst"
    if ilp_method == "pcst":
        G = nx.to_undirected(G)
        optG = imp_nx.read(G)
        m = p.create_model(optG, forced_terminals=[root], weight='weight')
        m.setParam('TimeLimit', timeout)
        m.optimize(p.callback_cycle)
        m = p.create_model(optG, forced_terminals=[], weight='weight')
        m.setParam('TimeLimit', timeout)
        m.optimize(p.callback_cycle)
        best_val = m.objVal
        solution = stp.extract_solution(optG, m)
        time_end = time.time()
        if m.Runtime + 1 > timeout:
            result_file.write("\nTimeout!\n")

    if ilp_method == "pcst_linear":
        G = nx.to_undirected(G)
        optG = imp_nx.read(G)
        m = stp.create_model(optG, forced_terminals=[root], weight='weight')
        m.setParam('TimeLimit', timeout)
        m.optimize()
        best_val = m.objVal
        solution = stp.extract_solution(optG, m)
        time_end = time.time()
        if m.Runtime + 1 > timeout:
            result_file.write("\nTimeout!\n")


    if ilp_method == "pcst_linear_tightened":
        G = nx.to_undirected(G)
        optG = imp_nx.read(G)
        m = plt.create_model(optG, forced_terminals=[root], weight='weight')
        m.setParam('TimeLimit', timeout)
        m.optimize()
        best_val = m.objVal
        solution = stp.extract_solution(optG, m)
        time_end = time.time()
        if m.Runtime + 1 > timeout:
            result_file.write("\nTimeout!\n")

    #%%
    translated = []
    for (u, v) in solution:
        try:
            translated.append(G.nodes[u]['origin'])
        except:
            pass
        try:
            translated.append(G.nodes[v]['origin'])
        except:
            pass

        if (u ,v) not in G_ox.edges():
            translated += G.edges[(u, v)]['path']
        else:
            translated.append((u, v))

    node_list1 = [u for (u, v) in translated]
    node_list2 = [v for (u, v) in translated]
    res_node_list = list(set(node_list1 + node_list2))
    res_terminals = [t for t in res_node_list if t in terminals]
    print(res_terminals)


    edge_colors = ['#ED0000' if (u, v) in translated or (v, u) in solution else '#AAA' for u, v in G_ox.edges()]
    edge_widths = [3 if (u, v) in translated else 1 for u, v in G_ox.edges()]

    ox.plot_graph(G_ox, figsize=(14, 10),
                  bgcolor='#FFF',
                  node_color=['green' if n == root and n in res_terminals else '#ED0000' if n in res_terminals else "blue" if n in res_node_list else 'white' for n in node_list],
                  node_size=[80 if n == root and n in res_terminals else 60 if n in res_terminals else 15 for n in node_list],
                  edge_color=edge_colors, edge_linewidth=edge_widths, save=True, filepath=path + "solution_with_reductions.png");

    #%% md

    ## Compare times used

    #%%
    print(solution)
    s = "\nTime to compute: " + str(time_end - time_start) + ". \n"
    s += "Obj. value reduction: " + str(best_val) + ". \n\n"
    result_file.write(s)
    print(s)

result = sum_of_prizes
res_nodes = set()
for (u, v) in solution:
    result += G.get_edge_data(u, v)['weight']
    res_nodes.add(u)
    res_nodes.add(v)
for u in G.nodes():
    if u in res_nodes:
        result -= G.nodes[u]['prize']
#result -= len(forced_terminals) * sum_of_profits
print(result)

print("Gurobi gap is:", m.MIPGap, "%")

