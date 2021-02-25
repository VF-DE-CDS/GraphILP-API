# +
from graphilp.imports import ilpgraph
from graphilp.imports import networkx as imp_nx
from graphilp.covering import min_vertexcover
import networkx as nx 
from gurobipy import *


# -

def maxMatch(G):
    print("Running Maximal Matching Heuristic...")
    """
    Implements the maximal matching heuristic in order the create an initial heuristic solution 
    for the optimzation process to take shorter.

    :param G: A Graph consisting of Edges and Nodes
    :type G: NetworkX Graph
    """

    edges = list(G.G.edges())
    chosenEdges = []
    chosenNodes = set()

    # The algorithm choses the first edge it can find and adds it to the list of selected Edges
    # In an inner loop it then removes all other edges that have the same starting Node or end Node as the chosen edge
    # This way, a maximal Matching is created.

    # Iterating through all edges in the Graph
    while len(edges) != 0:
        # Defining current  edge, startNode of the Edge and endNode of the Edge
        edge = edges[0]
        startNode = int(edges[0][0])
        endNode = int(edges[0][1])
        
        # Define bigger of the both Nodes to have a stopping criterion when working with sorted Node Lists
        biggestNode = max(startNode, endNode)

        # Add the chosen Edge to the chosenEdges List, i.e. the list that is returned in the end
        chosenEdges.append((startNode, endNode))

        # Add all chosen Nodes to the chosenNodes Set
        chosenNodes.add(startNode)
        chosenNodes.add(endNode)

        # Remove the current edge from the list of edges that still have to be iterated over
        edges.remove(edge)

        edgesCopy = list.copy(edges)

        # Inner Loop. Remove all other edges connected to the startNode or endNode.
        for e in edgesCopy:
            curEdgeStart = e[0]
            curEdgeEnd = e[1]

            if (curEdgeStart == startNode or curEdgeEnd == startNode or curEdgeStart == endNode or curEdgeEnd == endNode):
                edges.remove(e)
            
            # Important for bigger, sorted Lists of Nodes.
            # Iterating over the whole copy of edges in order to find potential edges that have to be deleted takes very long
            # By inserting a break, one can skip iterating over the remaining list as soon as the algorithm reached
            # the last line that is important for the currently selected Nodes.
            if curEdgeStart > biggestNode and curEdgeEnd > biggestNode:
                break

    return chosenNodes


def approxLP(G):
    print("Running LP Approx...")
    """ Create a LP for the minimum vertex cover problem as a method of approximation.
    The Linear relaxation is easier to solve and should thus be done very fast. Depending on how large the floating point
    of the continuous decision variable is, the value of a Binary variable that defines whether a Node is selected or not is chosen. 
    
    :param G: a weighted ILPGraph                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        

    # Add variables for edges and nodes    
    node_list = list(G.G.nodes())
    nodes = len(node_list)
    x = {}

    # Define decision Variables. The continuous variable may take any continuous value between and including 0 and 1.
    for i in range(nodes):
        x[node_list[i]] = m.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 1)

    m.update()            

    # The objective is to minimize the amount of Nodes we need for a valid Vertex Cover
    m.setObjective(sum(x[i] for i in node_list), GRB.MINIMIZE)

    # Create constraints    
    # for every edge, at least one Node / Vertex must be selected into a vertex cover of G    
    for (u, v) in G.G.edges():            
        m.addConstr(x[int(u)] + x[int(v)] >= 1 )    

    m.optimize()

    # Extract the actual solution from the approximation. If the value of the continuous variable is larger or equal 0.5, we assume the Node to be in an
    # optimal solution. All other cases are assumed not to lie in the optimal solution.
    solVars = m.getVars()
    chosenNodes = set()
    for i in range(len(solVars)):
        if solVars[i].X >= 0.5:
            chosenNodes.add(i + 1)
    return chosenNodes

""" if __name__ == '__main__':
    
    createApproximation(G)
    maximalMatching(G) """
