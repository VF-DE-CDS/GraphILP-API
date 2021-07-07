"""
Reduction technique that uses a greedy approach to solve the PCST problem. The technique comes from the paper [1]:
Leitner, Markus, et al.
"A dual ascent-based branch-and-bound framework for the prize-collecting Steiner tree and related problems."
INFORMS Journal on Computing 30.2 (2018): 402-420.

The breadth search required to find the lower bound comes from the paper [2]:
Pajor, Thomas, Eduardo Uchoa, and Renato F. Werneck.
"A robust and scalable algorithm for the Steiner problem in graphs."
Mathematical Programming Computation 10.1 (2018): 69-118.
"""

import networkx as nx
from graphilp.network.reductions import pcst_utilities as pcst_utilities


def parse_to_apcstp(G):
    """
    Creates an instance of the APCSTP by converting an undirected graph into two directed ones.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    G_directed = G.to_directed()
    return G_directed


def terminals_to_leaves(G: nx.DiGraph, root):
    """
    Transforms every terminal except the root into a leaf by inserting a new node between the terminal and all
    adjacent nodes. (Preprocessing step described in [1]
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: Integer representing the root node
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    terminals = pcst_utilities.compute_terminals(G)
    terminals = [t for t in terminals if t != root]
    new_node = max(G.nodes()) + 1
    for terminal in terminals:
        G.add_nodes_from([(new_node, {'prize': G.nodes[terminal]['prize']})])
        G.add_edge(terminal, new_node, weight=0)
        G.nodes[terminal]['prize'] = 0
        # Change the ids of the new node and the terminal in order to keep track of the right terminals
        mapping = {new_node: terminal, terminal: new_node}
        G = nx.relabel_nodes(G, mapping)
        new_node += 1
    return G


def leaves_to_terminals(G: nx.DiGraph, root):
    """
    Translates back the terminals transformed into a leave in the beginning
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: Integer representing the root node
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    terminals = pcst_utilities.compute_terminals(G)
    terminals = [t for t in terminals if t != root]
    for terminal in terminals:
        i = list(G.in_edges(terminal))[0][0]
        mapping = {i: terminal, terminal: i}
        G = nx.relabel_nodes(G, mapping)
        G.nodes[terminal]['prize'] = G.nodes[i]['prize']
        G.remove_node(i)
    return G


def compute_steiner_cut(G: nx.DiGraph, k, active_terminals, root, lb):
    """
    This routine searches for a cut for a given node k using a breath first search.
    The calculation is divided into 3 parts.
    The implementation is described in [2].
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param k: Node for which the cut is calculated
    :param active_terminals: A list of all active Terminals
                            (Terminals with positive potential profit and not connected to the root)
    :param root: Integer representing the root node
    :param lb: Intermediate lower bound
    :return: delta: Minimum residual capacity
    :return: lb: Lower bound
    """

    def pass1(G, k, active_terminals, root):
        """
        Breadth-first search, which only considers saturated incoming arcs.
        :return:
            s: Set containing all vertices in the cut
            l: List of all arcs
        """
        queue = [k]
        s = set()
        l = set()
        while queue:
            v = queue.pop(0)
            for (neighbour, node) in G.in_edges(v):
                s.add(node)
                l.add((neighbour, node))
                if G.get_edge_data(neighbour, node).get('reduced_costs') == 0 and neighbour not in s:
                    queue.append(neighbour)
                    # k does not define a root component (is no longer an active Terminal)
                    if neighbour in active_terminals or neighbour == root:
                        return None, None
        return s, l

    def pass2(l, s, k):
        """
        Traverses the list of arcs in the root component and deletes all edges that are completely contained in the
        root component. Picks the minimum residual capacity among all edges.
        :return: l: List only containing valid arcs (Arcs that start outside of the cut and end in the cut)
        :return: delta: Minimum residual capacity
        """

        l = [(u, v) for (u, v) in l if u not in s]
        delta = min([G.get_edge_data(u, v).get('reduced_costs') for (u, v) in l])
        delta = min(delta, G.nodes[k]['pi'])
        G.nodes[k]['pi'] -= delta
        return l, delta

    def pass3(G, delta, l):
        """
        Reduces the residual capacity of each arc in l by delta.
        """
        for (u, v) in l:
            G.edges[(u, v)]['reduced_costs'] -= delta

    s, l = pass1(G, k, active_terminals, root)
    if s is None:  # k does not define a root component (is no longer an active Terminal)
        return None, lb
    l, delta = pass2(l, s, k)
    pass3(G, delta, l)
    lb += delta
    return delta, lb


def dual_ascent(G: nx.DiGraph, root):
    """
    Main routine of the Dual Ascent algorithm.
    The routine is described in [1].
    The goal is to obtain a lower bound by connecting all terminals greedy to the root.
    If the connection cost is greater than the potential profit, the connection attempt for that terminal is aborted.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: Integer representing the root node
    :return: lb: The lower Bound for the whole graph
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    # Initialization of lower bound, reduced costs, pi (potential profit) and active_terminals
    terminals = pcst_utilities.compute_terminals(G)
    lb = 0  # lower bound
    for e in G.edges:
        G.edges[e]['reduced_costs'] = G.edges[e]['weight']
    for t in terminals:
        G.nodes[t]['pi'] = G.nodes[t]['prize']
    ta = [t for t in terminals if t != root]  # active terminals
    # main loop
    while len(ta) != 0:
        # TODO: There is no queue to optimally select the terminals one after the other
        k = ta[0]  # Chose active terminal
        delta, lb = compute_steiner_cut(G, k, ta, root, lb)  # compute Steiner cut
        # k is no longer an active terminal
        if delta is None or G.nodes[k]['pi'] <= 0:
            ta.remove(k)
    return lb


###########################################################
# All the following reduction techniques are taken from [1].
###########################################################


def test1(G, lower_bound, upper_bound, root):
    """
    Deletes all edges for which the lower bound > upper bound.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param lower_bound: Lower bound computed by the dual ascent routine
    :param upper_bound: Upper bound computed by pcst-fast
    :param root: Integer representing the root node
    """
    terminals = [t for t in pcst_utilities.compute_terminals(G) if t != root]
    to_be_deleted = []
    for (i, j) in G.edges:
        distance_reduced = nx.shortest_path_length(G, root, i, weight='reduced_costs')
        reduced_costs = G.get_edge_data(i, j)['reduced_costs']
        dist_terminal = pcst_utilities.d_nearest_terminals(G, j, terminals, edge_weight='reduced_costs')[0]
        # Sometimes there is a problem because of rounding, so I subtract 0.001
        if lower_bound + distance_reduced + dist_terminal + reduced_costs - 0.001 > upper_bound:
            to_be_deleted.append((i, j))
    G.remove_edges_from(to_be_deleted)


def test2(G, lower_bound, upper_bound, root):
    """
    Deletes all nodes for which the lower bound > upper bound.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param lower_bound: Lower bound computed by the dual ascent routine
    :param upper_bound: Upper bound computed by pcst-fast
    :param root: Integer representing the root node
    """
    terminals = [t for t in pcst_utilities.compute_terminals(G) if t != root]
    nodes = [v for v in G.nodes if v != root]
    for i in nodes:
        try:
            distance_reduced = nx.shortest_path_length(G, root, i, weight='reduced_costs')
            dist_terminal = pcst_utilities.d_nearest_terminals(G, i, terminals, edge_weight='reduced_costs')[0]
        except nx.exception.NetworkXNoPath:
            G.remove_node(i)
            continue
        # Sometimes there is a problem because of rounding, so I subtract 0.001
        if lower_bound + distance_reduced + dist_terminal - 0.001 > upper_bound:
            G.remove_node(i)


# TODO: Not used right now, because it has to be implemented in the ILP too
def test3(G, lower_bound, upper_bound, root):
    """
    Determines terminals, which must be mandatory in the solution.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param lower_bound: Lower bound computed by the dual ascent routine
    :param upper_bound: Upper bound computed by pcst-fast
    :param root: Integer representing the root node
    :return: oList of all terminals that are mandatory
    """
    terminals = [t for t in pcst_utilities.compute_terminals(G) if t != root]
    fixed_terminals = []
    for t in terminals:
        if lower_bound + G.nodes[t]["pi"] > upper_bound:
            fixed_terminals.append(t)
    return fixed_terminals


def test4(G):
    """
    Removes an edge if there is a shorter path for it.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    remove_edges = []
    for (i, j) in G.edges:
        if nx.shortest_path_length(G, i, j, weight='weight') < G.get_edge_data(i, j)["weight"]:
            remove_edges.append((i, j))
    G.remove_edges_from(remove_edges)


def test5(G):
    """
    Merges two nodes
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    for (i, j) in G.edges():
        # Counterpart of the edge has already been deleted
        if G.get_edge_data(i, j) is None or G.get_edge_data(j, i) is None or G.get_edge_data(i, j)['weight'] != \
                G.get_edge_data(j, i)['weight']:
            continue
        edge_cost = G.get_edge_data(i, j)['weight']
        incoming_edges_i = [G.get_edge_data(u, v)['weight'] for (u, v) in G.in_edges(i)]
        incoming_edges_j = [G.get_edge_data(u, v)['weight'] for (u, v) in G.in_edges(j)]
        if edge_cost < min(G.nodes[i]['prize'], G.nodes[j]['prize']) and edge_cost == min(
                incoming_edges_i) and edge_cost == min(incoming_edges_j):
            new_prize = G.nodes[i]['prize'] + G.nodes[j]['prize'] - edge_cost
            G = nx.contracted_nodes(G, i, j)
            G.nodes[i]['prize'] = new_prize


def dual_ascent_tests(G, root):
    """
    Routine for all the Voronoi diagram reduction tests
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: integer representing the root of the graph if -1 there is no root
    :return:
    """
    G = parse_to_apcstp(G)
    G = terminals_to_leaves(G, root)
    # Compute the global upper bound
    upper_bound = pcst_utilities.compute_upper_bound(G, root)
    # Compute the overall lower bound
    lower_bound = dual_ascent(G, root)
    # Apply reduction techniques
    test2(G, lower_bound, upper_bound, root)  # It's a lot faster to first compute test2
    test1(G, lower_bound, upper_bound, root)
    # TODO: Really use test3 (With Gurobi user cuts?)
    #fixed_terminals = test3(G, lower_bound, upper_bound, root)
    G = leaves_to_terminals(G, root)
    test4(G)
    test5(G)
    G = G.to_undirected()
    return G
