"""
Geometric reduction technique to solve the PCST.
The techniques come from the paper "Reduction techniques for the prize collecting Steiner tree problem
and the maximum-weight connected subgraph problem"
by Daniel Rehfeldt, Thorsten Koch and Stephen J. Maher from 2018
"""

import networkx as nx
from graphilp.network.reductions import pcst_utilities as pcst_utilities


def voronoi_diagram(G):
    """
    Divides the entire graph into different partitions, with one partition being created for each terminal.
    Each node is assigned to the partition to which the associated terminal is closest.

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return: Dictionary with terminals as keys and associated nodes as values
    """
    terminals = pcst_utilities.computeTerminals(G)
    diagram = nx.voronoi_cells(G, terminals, weight='weight')
    if 'unreachable'in diagram:
        G.remove_nodes_from(list(diagram['unreachable']))
        diagram.pop('unreachable')
    return diagram

def pcradius(G, diagram):
    """
    Specifies for each partition the minimum cost of including the partition's terminal in the solution.
    (Minimum from the prophet of the terminal and the minimum cost to reach the terminal from outside the partition.)

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param diagram: A dictionary of partitions of the graph
    :return: Dictionary with terminals as keys and minimum costs as values
    """
    radius = {}
    for cell in diagram:
        profit = G.nodes[cell]['prize']
        path = float('inf')
        for node in diagram[cell]:
            neighbours = [n for n in G.neighbors(node) if n not in diagram[cell]]
            for neighbour in neighbours:
                temp_path = nx.shortest_path_length(G, source=cell, target = neighbour, weight='weight')
                path = min(path, temp_path)
        radius[cell] = min(path, profit)
    return radius

def isSameBase(v, w, diagram):
    """
    Checks whether two nodes w and v are in the same partition.

    :param v: Integer representing node1
    :param w: Integer representing node1
    :param diagram: Dictionary representin partitions
    :return: Boolean if the nodes are in the same partition
    """
    for terminal in diagram:
        partiton = diagram[terminal]
        if v in partiton and w in partiton:
            return True
    return False


def dNearestTerminals(G, source, terminals, numberOfNearestTerminals = 1, duin=True):
    """
    Returns the nearest terminals for a given node

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param source: integer representing the eource node
    :param terminals: list of all terminals of the underlying graph
    :param numberOfNearestTerminals: the desired number of nearest terminals
    :param duin: if true and source is a terminal itself, source is added to the list of the nearest terminals
    :return:
    """

    shortestPaths = nx.shortest_path_length(G, source, weight='weight')
    if duin:
        shortestPathsTerminals = {k: v for k, v in shortestPaths.items() if k in terminals}
    else:
        shortestPathsTerminals = {k: v for k, v in shortestPaths.items() if k in terminals and k != source}
    return sorted(list(shortestPathsTerminals.values()))[0:numberOfNearestTerminals]


def proposition13(G, radius, upperBound):
    """
    Deletes all nodes with which the solution would be worse than the upper bound found with PCST-fast

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param radius: dictionary which saves the minimum cost of including a partition
    :param upperBound: worst possible solution
    """
    terminals = pcst_utilities.computeTerminals(G)
    nodes = [v for v in G.nodes if v not in terminals]
    for node in nodes:
        dNearestTerminal = pcst_utilities.dNearestTerminalsRoot(G, node, terminals, numberOfNearestTerminals=2)
        dNearestTerminal = list(dNearestTerminal.values())
        lowerBound = sum(radius[0:-2]) + sum(dNearestTerminal)
        if lowerBound > upperBound:
            G.remove_node(node)


def corollary14(G, radius_list, radius_dict, upperBound):
    terminals = pcst_utilities.computeTerminals(G)
    terminals = [t for t in terminals]
    for t in terminals:
        radius_list.sort()
        radius_list.remove(radius_dict.get(t))
        radius_list.insert(0, radius_dict.get(t))
        dNearestTerminal = pcst_utilities.dNearestTerminals(G, t, terminals, duin=False)
        #Für den Fall, dass das Terminal mit keinem anderen Terminal verbunden ist kann ich das Terminal direkt löschen, da wir für das Korollar von min 2 Terminals ausgehen
        if len(dNearestTerminal) == 0:
            G.remove_node(t)
        else:
            lowerBound = sum(radius_list[1:-1]) + sum(dNearestTerminal)
            if lowerBound -0.001 > upperBound:
                G.remove_node(t)

def proposition15(G, radius, radius_dict, upperBound):
    terminals = pcst_utilities.computeTerminals(G)
    term_deg2 = [t for t in terminals if G.degree[t] >= 2]
    res_nodes = []
    for t in term_deg2:
        radiusl = radius.copy()
        radius.remove(radius_dict.get(t))
        radius.insert(0, radius_dict.get(t))
        dNearestTerminal = dNearestTerminals(G, t, terminals, 2)
        lowerBound = sum(radius[1:-2]) + sum(dNearestTerminal)
        if lowerBound > upperBound:
            res_nodes.append(t)
    radius.sort()
    return res_nodes

def proposition17(G, radius, upperBound, diagram):
    terminals = pcst_utilities.computeTerminals(G)
    edges_to_remove = []
    for (v, w) in G.edges:
        dNearestTerminal_v = pcst_utilities.dNearestTerminals(G, v, terminals, numberOfNearestTerminals=2)
        dNearestTerminal_w = pcst_utilities.dNearestTerminals(G, w, terminals, numberOfNearestTerminals=2)
        if len(dNearestTerminal_w) < 2 or len(dNearestTerminal_v) < 2:
            edges_to_remove.append((v, w))
            continue
        sameBase = isSameBase(v, w, diagram)
        if not sameBase:
            lowerBound = sum(radius[0:-2]) + dNearestTerminal_v[0] + dNearestTerminal_w[0] + G.get_edge_data(v, w).get('weight')
        else:
            lowerBound = G.get_edge_data(v, w).get('weight') + \
                         min(dNearestTerminal_v[0] + dNearestTerminal_w[1], dNearestTerminal_v[1] + dNearestTerminal_w[0]) + \
                         sum(radius[0:-2])
        if lowerBound - 0.001 > upperBound:
            edges_to_remove.append((v, w))
    G.remove_edges_from(edges_to_remove)

def proposition18(G, radius, upperBound):
    terminals = pcst_utilities.computeTerminals(G)
    nodes = [n for n in G.nodes if G.degree[n] >= 3]
    res_nodes = []
    for n in nodes:
        nearestTerminals = dNearestTerminals(G, n, terminals, 3)
        lowerBound = sum(nearestTerminals) + sum(radius[0:-3])
        if lowerBound > upperBound:
            res_nodes.append(n)
    return res_nodes

def reductionTechniques(G, root=-1):
    """
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: integer representing the root of the graph if -1 there is no root
    :return:
    """
    # Use PCST-fast to compute an upper bound
    upperBound = pcst_utilities.computeUpperBound(G, root)
    # Partitioning the graph and computing the pcradius for each partition
    diagram = voronoi_diagram(G)
    radius_dict = pcradius(G, diagram)
    radius_list = list(radius_dict.values())
    radius_list.sort()
    # Use the propositions and corollaries suggested in the underlying paper
    proposition13(G, radius_list, upperBound)
    corollary14(G, radius_list, radius_dict, upperBound)
    term_deg2 = proposition15(G, radius_list, radius_dict, upperBound)
    proposition17(G, radius_list, upperBound, diagram)
    nodes_deg3 = proposition18(G, radius_list, upperBound)
    # Delete components not connected to the root #TODO: Find solution
    if root != -1:
        nodes = []
        for v in G.nodes:
            try:
                nx.shortest_path(G, root, v)
            except:
                nodes.append(v)
        G.remove_nodes_from(nodes)
    return term_deg2, nodes_deg3