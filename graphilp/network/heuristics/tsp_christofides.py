from networkx import minimum_spanning_tree, subgraph_view, eulerian_circuit
from graphilp.matching import perfect
from graphilp.imports import networkx as nximp
from gurobipy import GRB


def get_heuristic(G, weight='weight'):
    """ Approximation to TSP by `Christofides's algorithm <https://en.wikipedia.org/wiki/Christofides_algorithm>`__

    Creates a TSP tour from a minimum weight spanning tree by applying a minimum weight perfect matching
    to the nodes of odd degree in the spanning tree. This gives a low-weight Eulerian subgraph.
    An `Euler tour <https://en.wikipedia.org/wiki/Eulerian_path>`__ in it can be used to create
    a TSP tour by skipping over vertices that are visited more than once.

    This is a 3/2-approximation to the metric TSP and hence also gives a lower bound.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost

    :return: a list of edges forming the approximate solution and a lower bound on the optimal solution

    Example:
        .. code-block::

            warmstart, lower_bound = tsp_christofides.get_heuristic(G)

            m = create_model(G, warmstart=warmstart, lower_bound=lower_bound)

    """
    # compute minimum spanning tree
    T = minimum_spanning_tree(G.G, weight=weight)

    # get all vertices of odd degree
    odd_degree = [n[0] for n in T.degree() if n[1] % 2 != 0]

    # work on the subgraph of G induced by the nodes of odd degree in the spanning tree
    odd_sub = G.G.subgraph(odd_degree)

    # retain only those edges which are not part of the spanning tree
    odd_sub_min_T = subgraph_view(odd_sub,
                                  filter_edge=lambda u, v: ((u, v) not in T.edges()) and ((v, u) not in T.edges()))

    # find a minimum weight perfect matching on the resulting subgraph
    ilpG = nximp.read(odd_sub_min_T)
    m = perfect.create_model(ilpG, weight='weight', direction=GRB.MINIMIZE)
    m.optimize()

    matching = perfect.extract_solution(ilpG, m)

    # combine spanning tree and matching to get an Eulerian graph
    MT = T.copy()
    MT.add_edges_from(matching)

    # find an Euler circuit in MT
    euler = eulerian_circuit(MT)
    tour = list(euler)

    # short-cut by skipping vertices that would be visited twice
    # (this is where the metric property is used)
    visited = set([tour[0][0]])
    final_tour = []
    pos = 0

    while len(visited) < G.G.number_of_nodes():
        current_node = tour[pos][0]
        next_node = tour[pos][1]

        while next_node in visited:
            pos += 1
            next_node = tour[pos][1]

        final_tour.append((current_node, next_node))
        visited.add(next_node)
        pos += 1

    # close tour
    final_tour.append((final_tour[-1][1], 0))

    # We get a 3/2 approximation, so 2/3 of its value would be a lower bound
    # 19/30 is a somewhat careful version
    lower_bound = 19 * sum([G.G.edges()[e][weight] for e in final_tour]) / 30.0

    return final_tour, lower_bound
