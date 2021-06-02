import networkx as nx

from network.reductions import pcst_utilities


def ntd1(G, terminals):
    """
    Delete all non-Terminals with degree one and their corresponding edges.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    """
    nodes_to_remove = [n[0] for n in G.nodes(data=True) if G.degree[n[0]] == 1 and n[0] not in terminals]
    G.remove_nodes_from(nodes_to_remove)




def ntd2(G, terminals):
    """
    Substitute all non-terminals of degree 2 and its incident edges by a new edge (After computation translate the edges back for visualising the solution)
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    :param root: An integer representing the root
    """
    nodes_to_remove = [n for n in G.nodes(data=True) if G.degree[n[0]] == 2 and n[0] not in terminals]
    for node in nodes_to_remove:
        if len(G.adj[node[0]]) > 1: #Sometimes adjacent nodes are already deleted, so that the node has only one neighbour left
            u, v = list(G.neighbors(node[0]))[0], list(G.neighbors(node[0]))[1]
            # To translate it back after computation
            old_edges = G.edges(node[0], data = True)
            new_path = []
            for e in old_edges:
                if 'path' in e[2]:
                    new_path += e[2]['path']
                else:
                    new_path.append(e[:2])
            edgelength = G.get_edge_data(node[0], u).get('weight') + G.get_edge_data(node[0], v).get('weight')
            if not G.has_edge(u,v) or G.has_edge(u, v) and G.get_edge_data(u, v).get('weight') > edgelength:
                G.add_edge(u, v, weight=edgelength, path = new_path)
        G.remove_node(node[0])



def td1(G, terminals, root):
    """
    Substitute or delete all terminals of degree 1 depending on the cost of the incident edge.
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param terminals: A list of all terminals
    :param root: An integer representing the root
    """
    candidates = [t for t in terminals if G.degree[t] == 1 and t != root]
    nodes_to_remove = []
    for t in candidates:
        neighbour = list(G.neighbors(t))[0]
        edgelength = G.get_edge_data(t, neighbour)['weight']
        profit = G.nodes[t]['prize']
        if profit <= edgelength:
            nodes_to_remove.append(t)
        else:
            G.nodes[neighbour]['prize'] += profit - edgelength
            G.nodes[neighbour]['origin'] = (t, neighbour)
            nodes_to_remove.append(t)
        G.remove_nodes_from(nodes_to_remove)

def td2(G, root):
    """

    :param G:
    :param root:
    :return:
    """
    terminals = pcst_utilities.computeTerminals(G)
    candidates = [t for t in terminals if G.degree[t] == 2 and t != root]
    #candidates = [n for n in G.nodes(data=True) if G.degree[n[0]] == 2 and len(G.adj[n[0]]) > 1 and n in terminals]
    nodes_to_remove = []
    for n in candidates:
        profit_candidate = G.nodes[n]["prize"]
        neighbors = list(G.neighbors(n))
        length_e1 = G.get_edge_data(n, neighbors[0])['weight']
        length_e2 = G.get_edge_data(n, neighbors[1])['weight']
        profit_terminals = [G.nodes[t]["prize"] for t in terminals if t != n]
        # Um zurückübersetzen zu können
        old_edges = G.edges(n, data=True)
        new_path = []
        for e in old_edges:
            if 'path' in e[2]:
                new_path += e[2]['path']
            else:
                new_path.append(e[:2])
        if profit_candidate <= min(length_e1, length_e2, max(profit_terminals)):
            nodes_to_remove.append(n)
            length_newEdge = length_e1 + length_e2 - profit_candidate
            G.add_edge(neighbors[0], neighbors[1], weight = length_newEdge, path = new_path)
    G.remove_nodes_from(nodes_to_remove)



def unconnectedComponent(G):
    """

    :param G:
    :return:
    """
    terminals = pcst_utilities.computeTerminals(G)
    terminal_nodes = [t for t in terminals]
    if nx.number_connected_components(G) > 1:
        for comp in list(nx.connected_components(G)):
            delete_component = True
            for n in comp:
                if n in terminal_nodes:
                    delete_component = False
            if delete_component == True:
                [G.remove_node(n) for n in comp]



def basic_reductions(G, root):
    terminals = pcst_utilities.computeTerminals(G)
    ntd1(G, terminals)
    ntd2(G, terminals)
    #td1(G, terminals, root)
    #td2(G, root)
    unconnectedComponent(G)

if __name__ == '__main__':
    if __name__ == '__main__':

        """
        G = nx.Graph()

           G.add_nodes_from([
               (1, {'prize': 2}),
               (2, {'prize': 2}),
               (3, {'prize': 2}),
               (4, {'prize': 1})
           ])

           G.add_edges_from([(1, 2, {'weight': 1}), (1, 3, {'weight': 1}), (2, 3, {'weight': 1}),
                             (1, 4, {'weight': 3})
                             ])
           roots = []
        """
        G = nx.Graph()

        G.add_nodes_from([
            (1, {'prize': 6}),
            (2, {'prize': 0}),
            (3, {'prize': 0}),
            (4, {'prize': 6}),
            (5, {'prize': 0}),
            (6, {'prize': 0}),
            (7, {'prize': 1}),
            (8, {'prize': 0}),
            (9, {'prize': 2})
        ])

        G.add_edges_from([(1, 2, {'weight': 3}), (1, 5, {'weight': 4}), (2, 3, {'weight': 1}),
                          (2, 4, {'weight': 4}), (3, 4, {'weight': 1}), (5, 6, {'weight': 2}),
                          (5, 7, {'weight': 1}), (6, 4, {'weight': 7}), (7, 8, {'weight': 2}),
                          (8, 4, {'weight': 3}), (7, 9, {'weight': 30})
                          ])
    print(G.number_of_edges())


    pcst_utilities.draw(G)
    basic_reductions(G)
    pcst_utilities.draw(G)





