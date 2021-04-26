def get_heuristic(G):
    """ Approximate solution to the minimum vertex cover problem via maximal matching heuristic

    This heuristic successively chooses an edge in the graph, adds its vertices to the vertex cover
    and then deletes all edges adjacent to these vertices because they are already covered.

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`

    :return: a list of vertices forming a vertex cover of G
    """
    warmstart = []
    G_copy = G.G.copy()

    # successively delete covered edges until all edges are covered
    while G_copy.number_of_edges() > 0:
        # choose an edge
        edge = list(G_copy.edges())[0]

        # add vertices of the edge to vertex cover
        for v in edge:
            warmstart.append(v)

        # remove all edges adjacent to the chosen edge
        remove_edges = list(G_copy.edges(edge))
        G_copy.remove_edges_from(remove_edges)

    return warmstart
