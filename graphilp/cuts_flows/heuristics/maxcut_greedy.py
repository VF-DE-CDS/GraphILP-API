# +
import networkx as nx

def getHeuristic(G, weight='weight'):
    """
        Max Cut Greedy Heuristic.
        The Heuristic greedily finds Nodes to add to either to Set A or Set B. 
        Returns the weight of the edges lying between Set A and Set B.
        
        :params G: A weighted networkx Graph
        :type G: Networkx Graph
        :return: Total weight of edges in Max - Cut solution, i.e. the weight of the edges lying between Set A and Set B
        :rtype: int
    """
    # Set initialization
    A = set()
    B = set()
    maxCut = 0
    
    edgelist = list(G.edges(data=True))
    if 'weight' in edgelist[0][2]:
        pass
    else:
        for edge in G.edges(data=True):
            edge[2]['weight'] = 1
            
    for node in G.nodes():
        # Finding neighbourhood of the Node
        neighbors = G[node]
        neighInA = 0
        neighInB = 0
        # For every node now decide to either add it to Set A or Set B.
        # This depends on the amount of neighbours of the node that are in either Set A or B.
        # So, first of all count the amount of neighbours in either Set.
        for k, v in neighbors.items():
            if k in A:
                neighInA += v['weight']
            elif k in B:
                neighInB += v['weight']
        # Depending on the amount of neighbours in either Set, decide whether to add the node to Set A or B.
        if neighInA > neighInB:
            B.add(node)
        else:
            A.add(node)

    # Calculate the edge boundary, i.e. the edges lying between A and B
    edgesBetween = nx.edge_boundary(G, A, B)
    
    # Sum over all edges in the boundary and get their total weight 
    for edge in edgesBetween:
        maxCut += G.edges[edge]['weight']
        
    # Return the total weight of the edge boundary
    return maxCut
    
# -


