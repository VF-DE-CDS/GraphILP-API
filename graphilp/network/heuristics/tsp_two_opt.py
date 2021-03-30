def iterate_inner(G, tour, length, cities, i):
    """ Try all ending points :math:`j` in the tour for swapping.
    """
    for j in range(i + 2, cities):
        new_tour = two_opt_swap(i, j, tour)
        new_length = find_tour_length(new_tour, G)

        if (new_length < length):
            cur_tour = new_tour
            best_length = new_length

            return cur_tour, best_length, True

    return tour, length, False


def iterate_outer(G, tour, length, cities):
    """ Try all starting points :math:`i` in the tour for swapping.
    """
    new_tour = list.copy(tour)
    best_length = length

    for i in range(1, cities - 2):
        new_tour, best_length, new_sol_found = iterate_inner(G, tour, length, cities, i)

        if new_sol_found:
            return new_tour, best_length, True
        else:
            continue

    return new_tour, best_length, False


def two_opt_swap(i, j, tour):
    r""" Swap two cities in the tour

    Replace the tour

    :math:`s \xrightarrow{p_{su}} u \rightarrow i \xrightarrow{p_{ij}} j \rightarrow v \xrightarrow{p_{ve}} e`

    by

    :math:`s \xrightarrow{p_{su}} u \rightarrow j \xrightarrow{p_{ji}} i \rightarrow v \xrightarrow{p_{ve}} e`
    """
    # Take all cities up to i and include them in normal order
    next_tour = list.copy(tour[:i+1])

    # Reverse the tour from i to j
    reversed_cities = list.copy(tour[i+1:j+1][::-1])

    # Simply add up the remaining cities in the normal order
    remaining_tour = list.copy(tour[j+1:])

    next_tour.extend(reversed_cities)
    next_tour.extend(remaining_tour)

    return next_tour


def find_tour_length(tour, G):
    """ Compute the length of a given tour
    """
    tour_length = 0
    for i in range(0, len(tour)-1):
        pos = tour[i]
        succ = tour[i+1]
        tour_length = tour_length + G.edges[(pos, succ)].get('weight', 1)

    return tour_length


def get_heuristic(G, tour, length):
    r""" 2 Opt - Improvement heuristic for the Traveling Salesman Problem

    Improve a tour, e.g., one returned from the Nearest Neighbour Heuristic.
    Do this by exchanging the role of two vertices :math:`i` and :math:`j` iteratively as follows if it leads to a shorter tour:

    Replace the tour

    :math:`s \xrightarrow{p_{su}} u \rightarrow i \xrightarrow{p_{ij}} j \rightarrow v \xrightarrow{p_{ve}} e`

    by

    :math:`s \xrightarrow{p_{su}} u \rightarrow j \xrightarrow{p_{ji}} i \rightarrow v \xrightarrow{p_{ve}} e`

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param tour: a list of edges describing a tour
    :param length: length of the tour

    :return: a list of edges forming the approximate solution and its length
    """
    # Main function of the model.

    # Extracting the nodes of the tour in order to be able to perform 2 - OPT
    # Starting node
    cities = len(G.G.nodes())
    tour_form = [tour[0][0]]
    for i in range(1, len(tour)):
        tour_form.append(tour[i][0])

    # Add ending node (which is the same as the starting node)
    tour_form.append(tour[0][0])

    # Intermediate save so we don't destroy the original tour
    new_tour = list.copy(tour_form)
    best_length = length

    new_sol_found = True
    while new_sol_found:
        new_tour, best_length, new_sol_found = iterate_outer(G.G, new_tour, best_length, cities)

    new_tour = list(zip(new_tour, new_tour[1:]))

    return new_tour, best_length
