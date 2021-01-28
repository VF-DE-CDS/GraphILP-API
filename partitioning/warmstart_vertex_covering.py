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

    edges = list(G.edges())
    print(edges)
    chosenEdges = []

    while len(edges) != 0:
        edgesCopy = list.copy(edges)

        edge = edges[0]
        startNode = edges[0][0]
        endNode = edges[0][1]

        chosenEdges.append(edge)
        edgesCopy.remove(edge)
        edges.remove(edge)
        for i in range(len(edgesCopy)):

            curEdgeStart = edgesCopy[i][0]
            curEdgeEnd = edgesCopy[i][1]

            if (curEdgeStart == startNode or curEdgeEnd == startNode or curEdgeStart == endNode or curEdgeEnd == endNode):
                edges.remove(edgesCopy[i])

    print(chosenEdges)



def createApproximation(G):
    """ Create a LP for the minimum vertex cover problem as a method of approximation                
    Arguments:              G -- a weighted ILPGraph                    
    Returns:                a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        
    # Add variables for edges and nodes    
    node_list = G.nodes()
    nodes = len(node_list)
    x = {}
    for i in range(nodes):
        x[i] = m.addVar()
    m.update()            
    m.setObjective(sum(x[i] for i in range(nodes)), GRB.MINIMIZE)
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.edges():            
        m.addConstr(x[int(u) - 1] + x[int(v) - 1] >= 1 )    
    for i in range(nodes):
        m.addConstr(x[i] <= 1)
        m.addConstr(x[i] >= 0)
    
    return m

if __name__ == '__main__':
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, r'test_instances\1-Insertions_4.col')
    G = imp_nx.col_file_to_networkx(path)
    maximalMatching(G)
    #m = createApproximation(G)
    #m.optimize()
    G2 = ilpgraph.ILPGraph()
    G2.setNXGraph(G) 
    
    m2 = min_vertexcover.createModel(G2)
    m2.optimize()
    vars = m.getVars()
    for i in range(30):
        print(vars[i].x)
    vars = m2.getVars()
    for i in range(30):
        print(vars[i].x)