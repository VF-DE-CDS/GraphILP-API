# +
import networkx as nx

def getHeurSol(G, weight='weight'):
    """
        Max Cut Greedy Heuristic
        
        :params G: A weighted networkx Graph
        :type G: Networkx Graph
        :return: Total weight of edges in Max - Cut solution
        :rtype: int
    """
    
    A = set()
    B = set()
    maxCut = 0

    for node in G.nodes():
        neighbors = G[node]
        neighInA = 0
        neighInB = 0
        for k, v in neighbors.items():
            if k in A:
                neighInA += v['weight']
            elif k in B:
                neighInB += v['weight']
        if neighInA > neighInB:
            B.add(node)
        else:
            A.add(node)

    edgesBetween = nx.edge_boundary(G, A, B)
    for edge in edgesBetween:
        maxCut += G.edges[edge]['weight']
    return maxCut
    
# -


