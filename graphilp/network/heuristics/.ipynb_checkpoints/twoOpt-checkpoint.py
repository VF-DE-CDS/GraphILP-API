# +
def iterateInner(distance, tour, length, cities, i):
    for j in range(i + 2, cities):
        newTour = twoOptSwap(i, j, tour)
        newLength = findTourLength(newTour, distance)
        if (newLength < length):
            curTour = newTour
            bestLength = newLength
            return curTour, bestLength, True

    return tour, length, False

def iterateOuter(distance, tour, length, cities):
    newTour = list.copy(tour)
    bestLength = length
    for i in range(1, cities - 2):
        newTour, bestLength, newSolFound = iterateInner(distance, tour, length, cities, i)

        if newSolFound:
            return newTour, bestLength, True
        else:
            continue
    return newTour, bestLength, False

def getSol(distance, tour, length, cities):
    newTour = list.copy(tour)
    bestLength = length
    
    while True:
        newTour, bestLength, newSolFound = iterateOuter(distance, newTour, bestLength, cities)
        print(bestLength)
        if newSolFound:
            continue
        else:
            break
    
    return newTour, bestLength

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

def findTourLength(tour, distance):
    tourLength = 0
    for i in range(0, len(tour)-1):
        pos = tour[i]
        succ = tour[i+1]
        tourLength = tourLength + distance[pos][succ]
    return tourLength   
