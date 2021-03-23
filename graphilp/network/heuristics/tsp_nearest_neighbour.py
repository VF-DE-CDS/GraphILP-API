def getHeuristic(G, weight='weight'):
    """ Nearest neighbour heuristic for TSP
    
    Create a tour by greedily moving to the nearest neighbour that has not yet been visited in each step.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph` 
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    
    :return: a list of edges forming the approximate solution and its length
    """
    current = 0
    length = 0.0
    visited = set([0])
    tour = []

    while len(visited) < G.G.number_of_nodes():
        neighbours = [(w[weight], i, j) for i, j, w in G.G.edges(current, data=True) if j not in visited]
        argmax = neighbours.index(min(neighbours))
        next_step = neighbours[argmax]

        current = next_step[2]
        visited.add(current)

        tour.append(next_step[1:])
        length += next_step[0]
        
    # close the tour
    tour.append((tour[-1][1], 0))
    length += G.G.edges[tour[-1]][weight]
    
    return tour, length