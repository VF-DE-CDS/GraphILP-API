from networkx import edge_boundary


def get_heuristic(G, weight='weight'):
    """ Max cut greedy heuristic

        The heuristic greedily assigns vertices to either Set A or Set B depending on which choice leads
        to the more expensive cut.

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param weight: name of the weight parameter in the edge dictionary of the graph

        :return: a pair cut_set, cut_cost of a subset of the vertices inducing a maximum weight cut
            and the cost of the cut
    """
    # set initialization
    A = set()
    B = set()

    for node in G.G.nodes():
        # find neighbourhood of the vertex
        neighbors = G.G[node]
        weight_to_A = 0
        weight_to_B = 0

        # for every node decide to either add it to Set A or Set B.
        # this depends on the total weight of edges from this node to either Set A or B.
        for neighbor in neighbors.keys():
            if neighbor in A:
                weight_to_A += G.G.edges[(node, neighbor)].get(weight, 1)
            elif neighbor in B:
                weight_to_B += G.G.edges[(node, neighbor)].get(weight, 1)

        # depending on the total weight of the edges to either set, decide whether to add the vertex to Set A or B.
        if weight_to_A > weight_to_B:
            B.add(node)
        else:
            A.add(node)

    # calculate the edge boundary, i.e. the edges lying between A and B
    edgesBetween = edge_boundary(G.G, A, B)

    # sum over all edges in the boundary and get their total weight
    cut_cost = 0

    for edge in edgesBetween:
        cut_cost += G.G.edges[edge].get(weight, 1)

    # return one of the sets and the total weight of the edge boundary
    return A, cut_cost
