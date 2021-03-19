# +
import networkx as nx

def getHeurSol(G):
    """
        Max Cut Greedy Heuristic
        
        :params G: A networkx Graph
        :type G: Networkx Graph
        :rtype: Amount of edges in the Max Cut
    """
    
    A = set()
    B = set()
    neighInA = 0
    neighInB = 0
    maxCut = 0

    for node in G.nodes():
        neighbors = G.neighbors(node)
        neighInA = 0
        neighInB = 0
        for neighbor in neighbors:
            if neighbor in A:
                neighInA += 1
            else:
                neighInB += 1
        if neighInA > neighInB:
            B.add(node)
        else:
            A.add(node)

    edgesBetween = nx.edge_boundary(G, A, B)

    for edge in edgesBetween:
        maxCut += 1
    return maxCut
    
