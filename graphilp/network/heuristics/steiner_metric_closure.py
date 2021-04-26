from networkx import Graph, dijkstra_path_length, dijkstra_path, minimum_spanning_tree
from itertools import combinations


def get_heuristic(G, terminals, weight='weight'):
    """ Approximation to the Steiner tree problem by metric closure

    Creates a minimum weight spanning tree in the metric closure of terminals in the graph.
    This is a 2-approximation to the Steiner tree problem and hence also gives a lower bound.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param terminals: a list of vertices that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost

    :return: a list of edges forming the approximate solution and a lower bound on the optimal solution

    Example:
        .. code-block::

            warmstart, lower_bound = steiner_metric_closure.getHeuristic(G, terminals)

            m = create_model(G, terminals, weight='length', warmstart=warmstart, lower_bound=lower_bound)
    """
    # create a graph (called the metric closure) with all terminals as vertices,
    # distance of a shortest path between each pair of terminals,
    # and actual shortest paths
    closure_edges = []
    for p in combinations(terminals, 2):
        distance = dijkstra_path_length(G.G, p[0], p[1], weight='length')
        path = dijkstra_path(G.G, p[0], p[1], weight='length')
        closure_edges.append((p[0], p[1], {'weight': distance, 'path': path}))

    closure_graph = Graph()
    closure_graph.add_edges_from(closure_edges)

    # compute a minimum weight spanning tree
    min_span = minimum_spanning_tree(closure_graph)

    # add all edges from paths represented by the edges in the spanning tree to warmstart
    # also computes the total length of the warmstart
    warmstart = []
    lower_bound = 0.0

    for e in min_span.edges():
        path = min_span.edges[e]['path']
        lower_bound += min_span.edges[e]['weight']
        for u, v in zip(path, path[1:]):
            warmstart.append((u, v))

    # this warmstart is a 2-approximation, so half its value is a lower bound to the problem
    return warmstart, lower_bound/2
