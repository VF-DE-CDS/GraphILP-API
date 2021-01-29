import sys, os
sys.path.append(os.getcwd())
from imports import ilpgraph, graph_parser
from imports import networkx as imp_nx
from covering import min_vertexcover
import networkx as nx 
from gurobipy import *

def maximalMatching(G):
    """
    Implements the maximal matching heuristic in order the create an initial heuristic solution 
    for the optimzation process to take shorter.

    :param G: A Graph consisting of Edges and Nodes
    :type G: NetworkX Graph
    """

    edges = list(G.G.edges())
    chosenEdges = []
    chosenNodes = set()
    while len(edges) != 0:
        edge = edges[0]
        startNode = int(edges[0][0])
        endNode = int(edges[0][1])

        chosenEdges.append((startNode, endNode))
        chosenNodes.add(startNode)
        chosenNodes.add(endNode)
        
        edges.remove(edge)
        edgesCopy = list.copy(edges)
        for i in range(len(edgesCopy)):

            curEdgeStart = edgesCopy[i][0]
            curEdgeEnd = edgesCopy[i][1]

            if (curEdgeStart == startNode or curEdgeEnd == startNode or curEdgeStart == endNode or curEdgeEnd == endNode):
                edges.remove(edgesCopy[i])
    print(chosenNodes)
    return chosenNodes


def createApproximation(G):
    """ Create a LP for the minimum vertex cover problem as a method of approximation                
    Arguments:              G -- a weighted ILPGraph                    
    Returns:                a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        
    # Add variables for edges and nodes    
    node_list = G.G.nodes()
    nodes = len(node_list)
    x = m.addVars(G.G.nodes(), vtype = GRB.BINARY)

    m.update()            
    m.setObjective(sum(x[i] for i in range(nodes)), GRB.MINIMIZE)
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges():            
        m.addConstr(x[int(u)] + x[int(v)] >= 1 )    
    for i in range(nodes):
        m.addConstr(x[i] <= 1)
        m.addConstr(x[i] >= 0)
    
    m.optimize()
    vars = m.getVars()
    chosenNodes = set()
    for i in range(len(vars)):
        if vars[i].X >= 0.5:
            chosenNodes.add(i + 1)
    return chosenNodes

if __name__ == '__main__':
    
    createApproximation(G)
    maximalMatching(G)