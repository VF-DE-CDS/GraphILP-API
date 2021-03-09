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

def twoOptImprov(distance, tour, length, cities):
    maximprove = 10000
    while maximprove > 0:
        maximprove = 0
        for i in range(cities-2):
            for j in range(i+2,cities):
                delta = distance[tour[i]][tour[i+1]]+distance[tour[j]][tour[j+1]]-distance[tour[i]][tour[j]]-distance[tour[i+1]][tour[j+1]]
            for k in range(j-i-1):
                delta=delta+distance[tour[j-k-1]][tour[j-k]]-distance[tour[j-k]][tour[j-k-1]]    
            if delta > maximprove:
                best_i = i
                best_j = j
                maximprove = delta
            if maximprove > 0:
                next_tour = []
                for k in range(best_i+1):
                    next_tour.append(tour[k])
                for k in range(best_j-best_i):
                    next_tour.append(tour[best_j-k])
                for k in range(cities-best_j):
                    next_tour.append(tour[best_j+k+1]) 
                length = length - maximprove
                tour = next_tour
    return tour, length