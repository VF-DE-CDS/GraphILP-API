# +
def iterateInner(G, tour, length, cities, i):
    for j in range(i + 2, cities):
        newTour = twoOptSwap(i, j, tour)
        newLength = findTourLength(newTour, G)
        if (newLength < length):
            curTour = newTour
            bestLength = newLength
            return curTour, bestLength, True

    return tour, length, False

def iterateOuter(G, tour, length, cities):
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
    tourLength = 0
    for i in range(0, len(tour)-1):
        pos = tour[i]
        succ = tour[i+1]
        tourLength = tourLength + G.edges[(pos, succ)]['weight']
    return tourLength   


def getHeuristic(G, tour, length, cities):
    """ 2 Opt - Improvement Heuristic for the Traveling Salesman Problem
    
    Improve a tour, e.g. one returned from a Nearest Neighbour Heuristic. Do this by picking two nodes,
    reversing the tour between and including the nodes and including it back into the tour.
    
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param tour: a list of edges describing a tour
    :param length: Length of the tour
    :param cities: The amount of cities to be visited
    :type G: :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :type tour: :py:class:`~networkx
        
    """
    # Main function of the model.
    
    # Extracting the nodes of the tour in order to be able to perform 2 - OPT
    # Starting node
    tourForm = [tour[0][0]]
    for i in range(1, len(tour)):
        tourForm.append(tour[i][0])
    # Add ending node (which is the same as the starting node)
    tourForm.append(tour[0][0])
    
    # Intermediate save so we don't destroy the original tour
    newTour = list.copy(tourForm)
    bestLength = length
    
    while True:
        newTour, bestLength, newSolFound = iterateOuter(G.G, newTour, bestLength, cities)
        print(bestLength)
        if newSolFound:
            continue
        else:
            break
    
    return newTour, bestLength
