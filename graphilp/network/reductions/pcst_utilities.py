import graphilp.network.reductions.pcst_fast_interface_temp as pcst
import matplotlib.pyplot as plt
import networkx as nx
import pcst_fast


def compute_minimization_result(sum_of_prizes, G, solution):
    """
    Converts the objective value of a maximization problem to the objective value of a minimization problem.
    (Used to compare results with benchmarks)
    :param sum_of_prizes: Sum of all the profits of all terminals in the input Graph
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param solution: List of edges in the solution
    :return: result: The objective value of the equivalent minimization problem
    """
    result = sum_of_prizes
    res_nodes = set()
    for (u, v) in solution:
        result += G.get_edge_data(u, v)['weight']
        res_nodes.add(u)
        res_nodes.add(v)
    for u in G.nodes():
        if u in res_nodes:
            result -= G.nodes[u]['prize']
    return result


def validate_solution(solution, G, term_orig, result):
    """
    Checks whether the objective value of a found solution can really be achieved and whether the solution is valid.
    :param solution: List of edges in the solution:
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param term_orig: Dictionary of terminals with their profits in the input graph
    :param result: Objective value of the minimization problem
    """
    H = nx.Graph()
    H.add_edges_from(solution)
    # Solution must be connected and a tree to be valid
    if not nx.is_connected(H):
        raise Exception("Solution is not connected")
    if not nx.is_tree(H):
        raise Exception("Solution is not a tree")
    check_sum = 0
    for (u, v) in H.edges:
        check_sum += G.get_edge_data(u, v)['weight']

    lost_profits = [p for (t, p) in term_orig if t not in H.nodes]
    check_sum += sum(lost_profits)

    if round(check_sum, 3) != round(result, 3):
        raise Exception("Checksum unequals result")


def show_graph_size(G, name, file=None):
    """ Print out properties of a graph on the console (or to a file)
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param name: a String in which state the graph is
    :param file: File to which the size of the graph is to be written
    """
    terminals = len([t for t in G.nodes() if G.nodes[t]['prize'] > 0])
    s = name + \
        "\nNumber of nodes: " + str(G.number_of_nodes()) + \
        "\nNumber of edges: " + str(G.number_of_edges()) + \
        "\nNumber of terminals: " + str(terminals) + \
        "\n#########################\n"
    if file is not None:
        file.write(s)
    print(s)


def compute_terminals(G):
    """ Computes all terminals (nodes with a profit > 0) in a given graph
     :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
     :return: list of integers representing the terminals
    """
    terminals = []
    for n in G.nodes:
        if G.nodes[n]['prize'] > 0:
            terminals.append(n)
    return terminals


def d_nearest_terminals(G, source, terminals, edge_weight='weight', numberOfNearestTerminals=1, duin=True):
    """
    Returns the nearest terminals for a given node
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param source: integer representing the source node
    :param terminals: list of all terminals of the underlying graph
    :param edge_weight: Underlyingedgelabel
    :param numberOfNearestTerminals: the desired number of nearest terminals
    :param duin: if true and source is a terminal itself, source is added to the list of the nearest terminals
    :return:
    """

    shortestPaths = nx.shortest_path_length(G, source, weight=edge_weight)
    if duin:
        shortestPathsTerminals = {k: v for k, v in shortestPaths.items() if k in terminals}
    else:
        shortestPathsTerminals = {k: v for k, v in shortestPaths.items() if k in terminals and k != source}
    return sorted(list(shortestPathsTerminals.values()))[0:numberOfNearestTerminals]


def pcst_to_rpcst(G):
    """
    Routine to include a root to an PCSTP instance.
    For the dual ascent reduction technique,
    it is not possible to insert a node with very high profit and connect it to all nodes.
    The transformation algorithm is taken from the following source:
    Rehfeldt, Daniel, and Thorsten Koch.
    "On the exact solution of prize-collecting Steiner tree problems." (2020).
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    terminals = compute_terminals(G)
    terminals_proper = [t for t in terminals if
                        G.nodes[t]['prize'] > min([e.get('weight') for e in list(G.adj[t].values())])]
    terminals_unproper = [t for t in terminals if
                          G.nodes[t]['prize'] <= min([e.get('weight') for e in list(G.adj[t].values())])]
    terminals_fixed = []
    m = sum([G.nodes[t]['prize'] for t in terminals_proper])
    G_r = G.copy()
    for v in G_r.nodes:
        if v not in terminals_unproper:
            G_r.nodes[v]['prize'] = 0
    j = min(terminals_proper, key=lambda x: G.nodes[x]['prize'])
    n = G_r.number_of_nodes() + 1
    G_r.add_nodes_from([(n, {'prize': 0})])
    terminals_fixed.append(n)
    for t in terminals_proper:
        id = t + n
        G_r.add_nodes_from([(id, {'prize': 0})])
        G_r.add_edges_from([(n, t, {'weight': m}), (t, id, {'weight': m})])
        terminals_fixed.append(id)
    for t in terminals_proper:
        if t == j:
            continue
        id = t + n
        G_r.add_edges_from(
            [(t, j + n, {'weight': m + G.nodes[j]['prize']}), (id, j + n, {'weight': m + G.nodes[t]['prize']})])
    return G_r, terminals_fixed, m, n


def compute_upper_bound(G, root):
    """ Uses the PCST-Fast heuristic to compute an global upper bound
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param root: an integer representing the root of the graph
    :return: an integer representing an upper bound on the optimal solution
    """
    terminals = compute_terminals(G)
    dfNodes, dfEdges = pcst.createDataframes(G)
    rootIndex, terminals_indeces, accesspoints_indeces = pcst.findIndeces(dfNodes, terminals, root)  # accesspoints)
    dfFinal, dfChanged = pcst.mergeDataFrames(dfNodes, dfEdges)
    edges, nodePrices, edgeCosts = pcst.dataframeToList(dfFinal, dfNodes, dfChanged)
    # Let PCST_fast do its magic, i.e. optimizing the problem setting
    result_nodes, result_edges = pcst_fast.pcst_fast(edges, nodePrices, edgeCosts, rootIndex, 1, 'strong', 0)
    resultingNodes, resultingEdges, newGraph, prizesList = pcst.reformatToGraph(result_nodes, result_edges, dfFinal,
                                                                                dfNodes)
    # Find the upper bound out of the computed solution
    upperBound = 0
    for i in terminals:
        if i not in list(resultingNodes['Node']):
            upperBound += G.nodes[i]['prize']
    # Computing the costs of the found solution:
    upperBound += resultingEdges['Costs'].sum()
    return upperBound


def draw(G, edgelabel='weight'):
    """
    Draws a given input graph.
    (Works only for very small graphs)
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :param edgelabel: Label of the edge that should be drawn
    :return:
    """
    pos = nx.spring_layout(G, k=2)
    costs = nx.get_edge_attributes(G, edgelabel)
    profit = nx.get_node_attributes(G, 'prize')
    nx.draw_networkx_nodes(G, pos, node_color='w', edgecolors='black')
    nx.draw_networkx_edges(G, pos, edgelist=G.edges())
    nx.draw_networkx_edge_labels(G, pos, font_size=7, edge_labels=costs)
    nx.draw_networkx_labels(G, pos, profit, font_size=5, font_color='r')
    # nx.draw(G, pos=pos, with_labels=True)
    plt.show()
