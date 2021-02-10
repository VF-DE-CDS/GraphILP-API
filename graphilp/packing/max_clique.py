from gurobipy import *
from itertools import combinations

def createModel(G):
    """ Create an ILP for the maximum clique problem
        
    :param G: a weighted bipartite ILPGraph

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = Model("graphilp_max_clique")
    
    # Add variables for edges and nodes
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    nodes = G.node_variables
    
    # Create constraints
    ## for every pair of nodes, they can only be in the max clique when there is an edge between them
    for (u, v) in combinations(G.G.nodes(), 2):
        is_edge = 1 if (u, v) in G.G.edges() else 0
        m.addConstr(nodes[u] + nodes[v] <= 1 + is_edge)

    # set optimisation objective: maximum weight matching (sum of weights of chosen edges)
    m.setObjective( gurobipy.quicksum(nodes), GRB.MAXIMIZE)
    
    return m

def extractSolution(G, model):
    """ Get a list of vertices comprising a maximal clique
    
    :param G: a weighted ILPGraph
    :param model: a solved Gurobi model for maximum clique

    :return: a list of vertices comprising a maximal clique
    """
    clique_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]
    
    return clique_nodes


