"""
Reduction technique that uses geometric properties of the underlying graph to solve the PCST.
The techniques come from the paper:
Rehfeldt, Daniel, Thorsten Koch, and Stephen J. Maher.
"Reduction techniques for the prize collecting Steiner tree problem and the maximum‐weight connected subgraph problem."
Networks 73.2 (2019): 206-233.
"""

import networkx as nx
from graphilp.network.reductions import pcst_basic_reductions as pcst_basic
from graphilp.network.reductions import pcst_utilities as pcst_utilities


def voronoi_diagram(G):
    """
    Divides the entire graph into different partitions, with one partition being created for each terminal.
    Each non terminal node is assigned to the partition to which the associated terminal is closest.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return: Dictionary with terminals as keys and associated nodes of the partition as values
    """
    terminals = pcst_utilities.compute_terminals(G)
    diagram = nx.voronoi_cells(G, terminals, weight='weight')
    if 'unreachable' in diagram:
        G.remove_nodes_from(list(diagram['unreachable']))
        diagram.pop('unreachable')
    return diagram


def pc_radius(G, diagram):
    """
    Specifies for each partition the minimum cost of the partition's terminal in the solution.
    (Minimum from the profit of the terminal and the minimum cost to reach the terminal from outside the partition.)
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param diagram: A dictionary of partitions of the graph
    :return: Dictionary with terminals as keys and pc_radius as values
    """
    pc_radius = {}
    for cell in diagram:
        profit = G.nodes[cell]['prize']
        radius = float('inf')
        for node in diagram[cell]:
            neighbours = [n for n in G.neighbors(node) if n not in diagram[cell]]
            for neighbour in neighbours:
                temp_path = nx.shortest_path_length(G, source=cell, target=neighbour, weight='weight')
                radius = min(radius, temp_path)
        pc_radius[cell] = min(radius, profit)
    return pc_radius


def is_same_base(v, w, diagram):
    """
    Checks whether two nodes w and v are in the same voronoi partition.
    :param v: Integer representing node 1
    :param w: Integer representing node 2
    :param diagram: Dictionary representing partitions
    :return: Boolean if the nodes are in the same partition
    """
    for terminal in diagram:
        partition = diagram[terminal]
        if v in partition and w in partition:
            return True
    return False


###############################################
# The following are all the reduction techniques
###############################################

def proposition13(G, pc_radius, upper_bound):
    """
    Deletes all non-terminal nodes with which the local lower bound would be worse than the global upper bound
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param pc_radius: list which saves the minimum cost of including a partition
    :param upper_bound: Global upper bound
    """
    terminals = pcst_utilities.compute_terminals(G)
    nodes = [v for v in G.nodes if v not in terminals]
    for node in nodes:
        d_nearest_terminal = pcst_utilities.d_nearest_terminals(G, node, terminals, number_nearest_terminals=2)
        d_nearest_terminal = list(d_nearest_terminal)
        lower_bound = sum(pc_radius[0:-2]) + sum(d_nearest_terminal)
        if round(lower_bound, 3) > round(upper_bound, 3):
            G.remove_node(node)


def corollary14(G, radius_dict, upper_bound):
    """
    Deletes all terminal nodes with which the local lower bound would be worse than the global upper bound
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param radius_dict: A dictionary with terminals as keys an the belonging pc_radius as values
    :param upper_bound: Global upper bound
    """
    terminals = pcst_utilities.compute_terminals(G)
    terminals = [t for t in terminals]
    for t in terminals:
        radius_list = list(radius_dict.values())
        radius_list.sort()
        radius_list.remove(radius_dict.get(t))
        radius_list.insert(0, radius_dict.get(t))
        d_nearest_terminal = pcst_utilities.d_nearest_terminals(G, t, terminals, duin=False)
        # In the case that the terminal is not connected to any other terminal delete the terminal directly,
        # because we assume min 2 terminals for the corollary
        if len(d_nearest_terminal) == 0:
            G.remove_node(t)
        else:
            lower_bound = sum(radius_list[1:-1]) + sum(d_nearest_terminal)
            if round(lower_bound, 3) > round(upper_bound, 3):
                G.remove_node(t)


def proposition15(G, radius_dict, upper_bound):
    """
   Deletes all terminal nodes with which the local lower bound would be worse than the global upper bound.
   This method is more specific than corollary 14.
   :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
       :param radius_dict: A dictionary with terminals as keys an the belonging pc_radius as values
    :param upper_bound: Global upper bound
   """
    terminals = pcst_utilities.compute_terminals(G)
    term_deg2 = [t for t in terminals if G.degree[t] >= 2]
    res_nodes = []
    for t in term_deg2:
        radius_list = list(radius_dict.values())
        radius_list.sort()
        radius_list.remove(radius_dict.get(t))
        radius_list.insert(0, radius_dict.get(t))
        d_nearest_terminal = pcst_utilities.d_nearest_terminals(G, t, terminals, 'weight', 2)
        lower_bound = sum(radius_list[1:-2]) + sum(d_nearest_terminal)
        if round(lower_bound, 3) > round(upper_bound, 3):
            res_nodes.append(t)
    return res_nodes


def proposition17(G, radius, upper_bound, diagram):
    """
    Deletes all edges with which the local lower bound would be worse than the global upper bound.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param radius: A list with terminals as keys an the belonging pc_radius as values
    :param upper_bound: Global upper bound
    :param diagram: Dictionary representing partitions
    """
    radius.sort()
    terminals = pcst_utilities.compute_terminals(G)
    edges_to_remove = []
    for (v, w) in G.edges:
        d_nearest_terminal_v = pcst_utilities.d_nearest_terminals(G, v, terminals, number_nearest_terminals=2)
        d_nearest_terminal_w = pcst_utilities.d_nearest_terminals(G, w, terminals, number_nearest_terminals=2)
        if len(d_nearest_terminal_w) < 2 or len(d_nearest_terminal_v) < 2:
            edges_to_remove.append((v, w))
            continue
        same_base = is_same_base(v, w, diagram)
        if not same_base:
            lower_bound = sum(radius[0:-2]) + d_nearest_terminal_v[0] + d_nearest_terminal_w[0] + \
                          G.get_edge_data(v, w).get('weight')
        else:
            lower_bound = G.get_edge_data(v, w).get('weight') + \
                         min(d_nearest_terminal_v[0] + d_nearest_terminal_w[1],
                             d_nearest_terminal_v[1] + d_nearest_terminal_w[0]) + \
                         sum(radius[0:-2])
        if round(lower_bound, 3) > round(upper_bound, 3):
            edges_to_remove.append((v, w))
    G.remove_edges_from(edges_to_remove)


def proposition18(G, radius, upper_bound):
    """
    Deletes all non terminals with degree >= 3 if the local lower bound would be worse than the global upper bound.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param radius: A list with terminals as keys an the belonging pc_radius as values
    :param upper_bound: Global upper bound
    """
    radius.sort()
    terminals = pcst_utilities.compute_terminals(G)
    nodes = [n for n in G.nodes if G.degree[n] >= 3]
    res_nodes = []
    for n in nodes:
        nearest_terminals = pcst_utilities.d_nearest_terminals(G, n, terminals, 'weight', 3)
        lower_bound = sum(nearest_terminals) + sum(radius[0:-3])
        if round(lower_bound, 3) > round(upper_bound, 3):
            res_nodes.append(n)
    return res_nodes


def reduction_techniques(G, root=-1):
    """
    Routine for all the Voronoi diagram reduction tests
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: integer representing the root of the graph if -1 there is no root
    :return:
    """
    # Use PCST-fast to compute an upper bound
    upper_bound = pcst_utilities.compute_upper_bound(G, root)
    # Partitioning the graph and computing the pc_radius for each partition
    diagram = voronoi_diagram(G)
    radius_dict = pc_radius(G, diagram)
    radius_list = list(radius_dict.values())
    radius_list.sort()
    # Use the propositions and corollaries suggested in the underlying paper
    proposition13(G, radius_list, upper_bound)
    corollary14(G, radius_dict, upper_bound)
    # TODO: The information is not used right now. Does it work with proposition 16?
    # TODO: Don't understand proposition 16, is it useful with prop 15?
    term_deg2 = proposition15(G, radius_dict, upper_bound)
    proposition17(G, radius_list, upper_bound, diagram)
    # TODO: The information is not used right now.
    nodes_deg3 = proposition18(G, radius_list, upper_bound)
    # Delete components not connected to the root
    pcst_basic.unconnected_component(G, root)
    return term_deg2, nodes_deg3
