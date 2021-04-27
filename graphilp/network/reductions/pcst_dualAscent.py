"""
Reduction technique that uses a greedy approach to solve the PCST problem. The technique comes from the paper
"A dual-ascent-based branch-and-bound framework for the prize-collecting Steiner tree and related problems" by
Markus Leitner, Ivana Ljubic, Martin Luipersbeck, and Markus Sinnl.
The breadth search required to find the lower bound comes from "A robust and scalable algorithm for the Steiner problem
in graphs" by Thomas Pajor, Eduardo Uchoa and Renato F. Werneck.
"""

import networkx as nx
import matplotlib.pyplot as plt
import graphilp.network.reductions.pcst_utilities as pcst_utilities

def parse_to_APCSTP(G):
    """
    Creates an instance of the APCSTP by converting an undirected graph into a directed one.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    G_directed = G.to_directed()
    return G_directed

def terminals_to_leaves(G: nx.DiGraph, root):
    """
    Transforms every terminal except the root into a leaf by inserting a new node between the terminal and all adjacent nodes.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: Integer representing the root node
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__

    """
    terminals = pcst_utilities.computeTerminals(G)
    terminals = [t for t in terminals if t != root]
    i = G.number_of_nodes() + 1
    for terminal in terminals:
        G.add_nodes_from([(i, {'prize': G.nodes[terminal]['prize']})])
        G.add_edge(terminal, i, weight=0)
        G.nodes[terminal]['prize'] = 0
        # Change the ids of the new node and the terminal in order to keep track of the right terminals
        mapping = {i: terminal, terminal: i}
        G = nx.relabel_nodes(G, mapping)
        i += 1
    return G

def leaves_to_terminals(G: nx.DiGraph, root):
    """
    Translates back the terminals previously transformed into a leave
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: Integer representing the root node
    :return: G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    terminals = pcst_utilities.computeTerminals(G)
    terminals = [t for t in terminals if t != root]
    for terminal in terminals:
        i = list(G.in_edges(terminal))[0][0]
        mapping = {i: terminal, terminal: i}
        G = nx.relabel_nodes(G, mapping)
        G.nodes[terminal]['prize'] = G.nodes[i]['prize']
        G.remove_node(i)
    return G


#Nach Pajor2018 3.2 Processing a root component
def bfs(G : nx.DiGraph, k, activeTerminals, root):
    """
    Looks for a given node to see if it belongs to the root component. Is divided into three different passes
    :param G:
    :param k:
    :param activeTerminals:
    :param root:
    :return:
    """
    def pass1(G, k, activeTerminals, root):
        """
        Breadth-first search, which only considers saturated incoming arcs.
        :return:
            s: Set containing all vertices in the cut
            l: List of arcs
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
                    # k does not define a root component
                    if neighbour in activeTerminals or neighbour == root:
                        return None, None
        return s, l

    def pass2(l, s):
        """
        Traverses the list of arcs in the root component and deletes all edges that are completely contained in the root component.
        Picks the minimum residual capacity among all edges.
        :return:
            l: list only containing valid arcs
            delta: minimum residual capacity
        """
        l = [(u, v) for (u, v) in l if u not in s]
        delta = min([G.get_edge_data(u, v).get('reduced_costs') for (u, v) in l])
        return l, delta

    def pass3(G, delta, l):
        """
        Reduces the residual capacity of each arc in l by delta.
        :return:
        """
        x = set()
        for (u, v) in l:
            G.edges[(u, v)]['reduced_costs'] -= delta
            if G.get_edge_data(u, v).get('reduced_costs') == 0:
                x.add(u)
        return x

    s, l = pass1(G, k, activeTerminals, root)
    if s == None:
        return None, G, None
    l, delta = pass2(l, s)
    x = pass3(G, delta, l)
    return x, G, delta


def dual_ascent(G : nx.DiGraph, root):
    #Initialization
    terminals = pcst_utilities.computeTerminals(G)
    lb = 0
    for e in G.edges:
        G.edges[e]['reduced_costs'] = G.edges[e]['weight']
    for t in terminals:
        G.nodes[t]['pi'] = G.nodes[t]['prize']
    ta = terminals
    if root in ta:
        ta.remove(root)
    #loop
    while len(ta) != 0:
        # TODO: Noch gibt es keine Queue, um die Terminals nacheinander zu behandeln
        k = ta[0]
        x, G, delta = bfs(G, k, ta, root)
        if x == None:
            ta.remove(k)
        else:
            #Hier sind alle Terminals in T_p?
            delta = min(delta, G.nodes[k]["pi"])
            G.nodes[k]["pi"] -= delta
            lb += delta
            if G.nodes[k]["pi"] == 0:
                ta.remove(k)
            #helpfunctions.draw(G)
    return lb, G

def test1(G, lowerBound, upperBound, root):
    terminals = [t for t in pcst_utilities.computeTerminals(G) if t != root]
    to_be_deleted = []
    for (i, j) in G.edges:
        distance_reduced = nx.shortest_path_length(G, root, i, weight='reduced_costs')
        reduced_costs = G.get_edge_data(i, j)['reduced_costs']
        distTerminal = pcst_utilities.dNearestTerminals(G, j, terminals, edgeweight='reduced_costs')[0]
        if lowerBound + distance_reduced + distTerminal + reduced_costs - 0.001 > upperBound:
            to_be_deleted.append((i, j))
    G.remove_edges_from(to_be_deleted)

def test2(G, lowerBound, upperBound, root):
    terminals = [t for t in pcst_utilities.computeTerminals(G) if t != root]
    nodes = [v for v in G.nodes if v != root]
    to_be_deleted = []
    for i in nodes:
        try:
            distance_reduced = nx.shortest_path_length(G, root, i, weight='reduced_costs')
            distTerminal = pcst_utilities.dNearestTerminals(G, i, terminals, edgeweight='reduced_costs')[0]
        except:
            G.remove_node(i)
            continue
        # Sometimes there is a problem because of floats so I subtract 0.001
        if lowerBound + distance_reduced + distTerminal - 0.001 > upperBound:
            G.remove_node(i)

def test3(G, lowerBound, upperBound, root):
    terminals = [t for t in pcst_utilities.computeTerminals(G) if t != root]
    fixed_terminals = []
    for t in terminals:
        if lowerBound + G.nodes[t]["pi"] > upperBound:
            fixed_terminals.append(t)
    return fixed_terminals

def test4(G):
    for (i, j) in G.edges:
        if nx.shortest_path_length(G, i, j, weight='weight') < G.get_edge_data(i, j)["weight"]:
            G.remove_edge((i, j))


def dual_ascent_tests(G, root):
    G = parse_to_APCSTP(G)
    G = terminals_to_leaves(G, root)
    lowerBound, G = dual_ascent(G, root)
    upperBound = pcst_utilities.computeUpperBound(G, root)
    test2(G, lowerBound, upperBound, root)
    test1(G, lowerBound, upperBound, root)
    fixed_terminals = test3(G, lowerBound, upperBound, root)
    G = leaves_to_terminals(G, root)

    return G, fixed_terminals
