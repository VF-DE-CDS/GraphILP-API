def nearNeighHeur(distance, cities):
    # nearest neighbor    
    position = 0
    tour = [0]
    length = 0
    for i in range(cities-1):
        nn = 0
        nd = 10000
        for j in range(cities):  
            if (j not in tour) and (distance[position][j]<nd):
                nd = distance[position][j]
                nn = j
        tour.append(nn)
        length = length + nd
        position = nn
    tour.append(0)
    length = length + distance[position][0]
    return tour, length
