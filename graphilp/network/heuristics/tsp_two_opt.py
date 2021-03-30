def iterateInner(G, tour, length, cities, i):
    """ Try all ending points :math:`j` in the tour for swapping.
    """
    for j in range(i + 2, cities):
        newTour = twoOptSwap(i, j, tour)
        newLength = findTourLength(newTour, G)
        
        if (newLength < length):
            curTour = newTour
            bestLength = newLength
            
            return curTour, bestLength, True

    return tour, length, False

def iterateOuter(G, tour, length, cities):
    """ Try all starting points :math:`i` in the tour for swapping.
    """
    newTour = list.copy(tour)
    bestLength = length
    
    for i in range(1, cities - 2):
        newTour, bestLength, newSolFound = iterateInner(G, tour, length, cities, i)

        if newSolFound:
            return newTour, bestLength, True
        else:
            continue
            
    return newTour, bestLength, False

def twoOptSwap(i, j, tour):
    r""" Swap two cities in the tour
    
    Replace the tour
    
    :math:`s \xrightarrow{p_{su}} u \rightarrow i \xrightarrow{p_{ij}} j \rightarrow v \xrightarrow{p_{ve}} e`
    
    by
    
    :math:`s \xrightarrow{p_{su}} u \rightarrow j \xrightarrow{p_{ji}} i \rightarrow v \xrightarrow{p_{ve}} e`
    """
    
    # Take all cities up to i and include them in normal order
    next_tour = list.copy(tour[:i+1])

    # Reverse the tour from i to j
    reversedCities = list.copy(tour[i+1:j+1][::-1])

    # Simply add up the remaining cities in the normal order
    remainingTour = list.copy(tour[j+1:])

    next_tour.extend(reversedCities)
    next_tour.extend(remainingTour)

    return next_tour

def findTourLength(tour, G):
    """ Compute the length of a given tour
    """
    tourLength = 0
    for i in range(0, len(tour)-1):
        pos = tour[i]
        succ = tour[i+1]
        tourLength = tourLength + G.edges[(pos, succ)].get('weight', 1)
        
    return tourLength   


def getHeuristic(G, tour, length):
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
    tourForm = [tour[0][0]]
    for i in range(1, len(tour)):
        tourForm.append(tour[i][0])

    # Add ending node (which is the same as the starting node)
    tourForm.append(tour[0][0])
    
    # Intermediate save so we don't destroy the original tour
    newTour = list.copy(tourForm)
    bestLength = length
    
    newSolFound = True
    while newSolFound:
        newTour, bestLength, newSolFound = iterateOuter(G.G, newTour, bestLength, cities)
        
    newTour = list(zip(newTour, newTour[1:]))
    
    return newTour, bestLength
