from gurobipy import *
from itertools import combinations

def createModel(G):
    r""" Create an ILP for the maximum clique problem
        
    :param G: a weighted bipartite ILPGraph

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP: 
        This formulation makes use of the connection between clique and vertex cover in the complement.
        It excludes as few nodes as possible from a clique but needs to exclude at least one node from each pair
        not connected by an edge.
        Vertex cover has a smaller integrality gap.
    
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{v \in V} x_v\\
            \text{s.t.} &&\\
            \forall (u, v) \in \bar{E}: x_u + x_v >= 1 && \text{(exclude at least one node from each unconnected pair)}\\
            \end{align*}
    """
    
    # Create model
    m = Model("graphilp_max_clique")
    
    # Add variables for edges and nodes
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    nodes = G.node_variables
    
    # Create constraints
    ## for every pair of nodes, at least one node must cover the edge
    for (u, v) in combinations(G.G.nodes(), 2):
        if (u, v) not in G.G.edges():
            m.addConstr(nodes[u] + nodes[v] >= 1)

    # set optimisation objective: minimum vertex cover
    m.setObjective( gurobipy.quicksum(nodes), GRB.MINIMIZE)
    
    return m

def extractSolution(G, model):
    """ Get a list of vertices comprising a maximal clique
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for maximum clique
            
        :return: a list of vertices comprising a maximal clique
    """
    clique_nodes = [node for node, node_var in G.node_variables.items() if node_var.X < 0.5]
    
    return clique_nodes


