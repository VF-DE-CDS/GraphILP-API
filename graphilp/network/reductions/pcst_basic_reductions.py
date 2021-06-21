import networkx as nx
from graphilp.network.reductions import pcst_utilities


# Reduction techniques that use basic properties of the graph.
# All reduction techniques described here are taken from the following paper:
# REHFELDT, Daniel; KOCH, Thorsten; MAHER, Stephen J.
# Reduction techniques for the prize collecting Steiner tree problem and the maximum‐weight connected subgraph problem.
# Networks, 2019, 73. Jg., Nr. 2, S. 206-233.

def ntd1(G, terminals):
    """
    Delete all non-terminals with degree one and their corresponding edges.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    """
    nodes_to_remove = [n for n in G.nodes if G.degree[n] == 1 and n not in terminals]
    G.remove_nodes_from(nodes_to_remove)


def ntd2(G, terminals):
    """
    Substitute all non-terminals of degree 2 and its incident edges by a new edge (After computation translate the 
    edges back for visualising the solution) 
    :param G: a `NetworkX graph  <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__ 
    :param terminals: A list of all terminals 
    """
    nodes_to_remove = [n for n in G.nodes if G.degree[n] == 2 and n not in terminals]
    for node in nodes_to_remove:
        if len(G.adj[node]) > 1:  # Sometimes adjacent nodes are already deleted, so that the node has only one
            # neighbour left
            u, v = list(G.neighbors(node))[0], list(G.neighbors(node))[1]
            # To translate it back after computation
            old_edges = G.edges(node, data=True)
            new_path = []

            for e in old_edges:
                if 'path' in e[2]:
                    new_path += e[2]['path']
                else:
                    new_path.append(e[:2])
            edge_length = G.get_edge_data(node, u).get('weight') + G.get_edge_data(node, v).get('weight')
            if not G.has_edge(u, v) or G.has_edge(u, v) and G.get_edge_data(u, v).get('weight') > edge_length:
                G.add_edge(u, v, weight=edge_length, path=new_path)
        G.remove_node(node)


def td1(G, terminals, root=None):
    """
    Substitute or delete all terminals of degree 1 depending on the cost of the incident edge.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    :param root: An integer representing the root
    """
    if root is None:
        # Without root the terminal with the biggest profit can't be deleted
        max_terminal = [t for t in terminals if G.nodes[t]['prize'] == max([G.nodes[t]['prize'] for t in terminals])][0]
        candidates = [t for t in terminals if G.degree[t] == 1 and t != root]
        if max_terminal in candidates:
            candidates.remove(max_terminal)
    else:
        # In the rooted case only the root can't be deleted
        candidates = [t for t in terminals if G.degree[t] == 1 and t != root]
    nodes_to_remove = []
    for t in candidates:
        neighbour = list(G.neighbors(t))[0]
        edge_length = G.get_edge_data(t, neighbour)['weight']
        profit = G.nodes[t]['prize']
        if profit <= edge_length:
            nodes_to_remove.append(t)
        else:
            G.nodes[neighbour]['prize'] += profit - edge_length
            # To be able to translate back you have to give the path to the neighbour node
            old_edges = G.edges(t, data=True)
            new_path = []
            for e in old_edges:
                if 'path' in e[2]:
                    new_path += e[2]['path']
                else:
                    new_path.append(e[:2])
            G.nodes[neighbour]['origin'] = new_path
            nodes_to_remove.append(t)
        G.remove_nodes_from(nodes_to_remove)


def td2(G, root):
    """
    Terminal of degree 2 can be substituted by an edge if its profit is too small to include the terminal-
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: An integer representing the root
    """
    terminals = pcst_utilities.compute_terminals(G)
    candidates = [t for t in terminals if G.degree[t] == 2 and t != root]
    nodes_to_remove = []
    for n in candidates:
        profit_candidate = G.nodes[n]["prize"]
        neighbors = list(G.neighbors(n))
        length_e1 = G.get_edge_data(n, neighbors[0])['weight']
        length_e2 = G.get_edge_data(n, neighbors[1])['weight']
        profit_terminals = [G.nodes[t]["prize"] for t in terminals if t != n]
        # To be able to translate it back
        old_edges = G.edges(n, data=True)
        new_path = []
        for e in old_edges:
            if 'path' in e[2]:
                new_path += e[2]['path']
            else:
                new_path.append(e[:2])
        if profit_candidate <= min(length_e1, length_e2, max(profit_terminals)):
            nodes_to_remove.append(n)
            length_new_edge = length_e1 + length_e2 - profit_candidate
            G.add_edge(neighbors[0], neighbors[1], weight=length_new_edge, path=new_path)
    G.remove_nodes_from(nodes_to_remove)


def unconnected_component(G, root=None):
    """
    Delete any component that does not contain terminals.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: An integer representing the root
    """
    terminals = pcst_utilities.compute_terminals(G)
    terminal_nodes = [t for t in terminals]
    if nx.number_connected_components(G) > 1:
        for comp in list(nx.connected_components(G)):
            delete_component = True
            for n in comp:
                if root is None:
                    if n in terminal_nodes:
                        delete_component = False
                else:
                    if n == root:
                        delete_component = False
            if delete_component:
                [G.remove_node(n) for n in comp]


def basic_reductions(G, root):
    """
    Calls all Basic Reductions one after the other
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: An integer representing the root
    """
    terminals = pcst_utilities.compute_terminals(G)
    ntd1(G, terminals)
    ntd2(G, terminals)
    td1(G, terminals, root)
    td2(G, root)
    unconnected_component(G, root)
