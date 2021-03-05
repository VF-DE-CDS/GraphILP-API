from gurobipy import *
from itertools import combinations

def createModel(G):
    """ Create an ILP for the maximum clique problem
        
    :param G: a weighted bipartite ILPGraph

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP: 
        .. math::
            :nowrap:

            \begin{align*}
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
        is_edge = 1 if (u, v) in G.G.edges() else 0
        if (is_edge == 0):
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


