import networkx as nx
import pcst_fast
import graphilp.network.reductions.pcst_fast_interface_temp as pcst
from gurobipy import Model, GRB, quicksum
import gurobipy
import time

def show_graph_size(G, name):
    """ Print out the individual properties of a graph on the console

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param name: a String in which state the graph is
    """
    terminals = len([t for t in G.nodes() if G.nodes[t]['prize'] > 0])
    s = name + \
        "\nNumber of nodes: " + str(G.number_of_nodes()) + \
        "\nNumber of edges: " + str(G.number_of_edges()) + \
        "\nNumber of terminals: " + str(terminals) + \
        "\n#########################"
    print(s)

def computeTerminals(G):
    """ Computes all terminals (nodes with a profit > 0) in a given graph

     :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
     :return: list of integers representing the terminals
    """
    terminals = []
    for node in G.nodes(data=True):
        if node[1]['prize'] > 0:
            terminals.append(node[0])
    return terminals

def computeUpperBound(G, root):
    """ Uses the PCST-Fast heuristic to compute an upper bound

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: an integer representing the root of the graph
    :return: an integer representing an upper bound on the optimal solution
    """
    terminals = computeTerminals(G)

    dfNodes, dfEdges = pcst.createDataframes(G)
    rootIndex, terminalsIndeces, accesspointsIndeces = pcst.findIndeces(dfNodes, terminals, root)  # accesspoints)
    dfFinal, dfChanged = pcst.mergeDataFrames(dfNodes, dfEdges)
    edges, nodePrices, edgeCosts = pcst.dataframeToList(dfFinal, dfNodes, dfChanged)

    # Let PCST_fast do its magic, i.e. optimizing the problem setting
    result_nodes, result_edges = pcst_fast.pcst_fast(edges, nodePrices, edgeCosts, rootIndex, 1, 'strong', 0)

    containedTerminals, containedAccesspoints = pcst.extractSolution(result_nodes, terminalsIndeces, accesspointsIndeces)
    resultingNodes, resultingEdges, newGraph, prizesList = pcst.reformatToGraph(result_nodes, result_edges, dfFinal, dfNodes)

    # Find the upper bound out of the computed solution
    upperBound = 0
    for i in terminals:
        if i not in list(resultingNodes['Node']):
            upperBound += G.nodes[i]['prize']
    # Computing the costs of the found solution:
    upperBound += resultingEdges['Costs'].sum()
    return upperBound


def gurobi(G, root, voronoi_active = False, term_deg2 = None, nodes_deg3 = None, dual_ascent_active = False, fixed_terminals = None):
    #try:
    # Jeder Knoten hat einen Profit, welcher über prize zu erhalten ist (Die meisten sind 0, hier haben nur 32 auch 2000 einen positiven Wert
    # print([n for n in G.nodes(data=True) if n[1]['prize'] > 0])
    edges = list(G.edges())
    node_list = list(G.nodes())
    #tst = set(edge_list)
    # Es werden alle Kanten gelöscht, die beidseitig sind. Warum?? (Sind hier auch nur 5 Stück von 3470
    edge_list, seen = [], set()
    for item in edges:
        t1 = tuple(item)
        if t1 not in seen:
            if tuple(reversed(item)) not in seen:
                seen.add(t1)
                edge_list.append(item)


    # dictionaries for nodes and edges:
    node_dict = dict(enumerate(node_list))
    edge_dict = dict(enumerate(edge_list))
    rev_node_dict = dict(zip(node_dict.values(), node_dict.keys()))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))
    # Set up problem in Gurobi
    m = Model("PCST")
    # m.Params.LazyConstraints = 1
    m.Params.threads = 3
    # create node variables and node label variables
    for node in node_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
        m.addVar(vtype=gurobipy.GRB.INTEGER, lb=1, ub=G.number_of_nodes(), name="label_" + str(node))
    # create edge variables
    for edge in edge_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[0]) + "_" + str(edge[1]))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[1]) + "_" + str(edge[0]))
    m.update()
    # Set objective
    m.setObjective(
        gurobipy.quicksum(
            [n[1]['prize'] * m.getVarByName("node_" + str(n[0])) for n in G.nodes(data=True) if n[1]['prize'] > 0]) \
        - gurobipy.quicksum(
            [G.edges[u, v]['weight'] * m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list]) \
        - gurobipy.quicksum(
            [G.edges[u, v]['weight'] * m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list]), \
        GRB.MAXIMIZE)
    # Equality constraints
    # Enforce a root
    m.addConstr(m.getVarByName("node_" + str(root)) == 1)

    # restrict number of edges
    m.addConstr(gurobipy.quicksum([m.getVarByName("node_" + str(node)) for node in node_list]) \
                - gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list]) \
                - gurobipy.quicksum([m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list]) == 1)
    m.update()


    # at most one direction per edge can be chosen
    for (u, v) in edge_list:
        m.addConstr(
            m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)) <= 1)

    # if edge is chosen, both adjacent nodes need to be chosen
    for (u, v) in edge_list:
        m.addConstr(
            2 * (m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u))) \
            - m.getVarByName("node_" + str(u)) \
            - m.getVarByName("node_" + str(v)) <= 0)
    m.update()

    # prohibit isolated vertices (Jeder Knoten muss mit mindestens einer Kante verbunden sein)
    for node in node_list:
        edge_vars = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if
                     (node == u) or (node == v)] \
                    + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if
                       (node == u) or (node == v)]

        m.addConstr(m.getVarByName("node_" + str(node)) - gurobipy.quicksum(edge_vars) <= 0)
    m.update()
    # enforce increasing labels
    n = G.number_of_nodes()
    for (u, v) in edge_list:
        m.addConstr(n * m.getVarByName("edge_" + str(v) + "_" + str(u)) + m.getVarByName("label_" + str(v)) \
                    - m.getVarByName("label_" + str(u)) >= 1 - n * (
                                1 - m.getVarByName("edge_" + str(u) + "_" + str(v))))
        m.addConstr(n * m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("label_" + str(u)) \
                    - m.getVarByName("label_" + str(v)) >= 1 - n * (
                                1 - m.getVarByName("edge_" + str(v) + "_" + str(u))))

    m.update()

    # allow only one arrow into each node
    for node in node_list:
        edges = [(u, v) for (u, v) in edge_list if v == node]
        edges += [(v, u) for (u, v) in edge_list if u == node]
        m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edges]) <= 1)

    ###########################################################################################################################################
    # Eigener Code

    if voronoi_active:
        # Proposition 15 Voronoi:
        for node in term_deg2:
            incident_edges = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if
                              (node == u) or (node == v)] \
                             + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if
                                (node == u) or (node == v)]
            m.addConstr(gurobipy.quicksum(incident_edges) <= 1)

        # Proposition 18 Voronoi:
        # nodes_deg3: Alle Knoten, deren Grad < als 3 sein muss
        for node in nodes_deg3:
            incident_edges = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if
                              (node == u) or (node == v)] \
                             + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if
                                (node == u) or (node == v)]
            m.addConstr(gurobipy.quicksum(incident_edges) <= 2)

    if dual_ascent_active:
        # Test 3: Alle fixed Terminals müssen in der Lösung enthalten sein:
        for t in fixed_terminals:
            m.addConstr(m.getVarByName("node_" + str(t)) == 1)

    ###########################################################################################################################################



    m.optimize()

    res_edges = [(u, v) for (u, v) in G.edges if m.getVarByName("edge_" + str(u) + "_" + str(v)).X > 0.1]
    res_edges += [(v, u) for (u, v) in G.edges if m.getVarByName("edge_" + str(v) + "_" + str(u)).X > 0.1]
    solution, seen  = [], set()

    for item in res_edges:
        if item not in seen:
            if reversed(item) not in seen:
                seen.add(item)
                solution.append(item)

    best_val = m.objVal
    return solution, best_val
