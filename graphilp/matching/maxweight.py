from gurobipy import *

def createModel(G):
    """ Create an ILP for maximum weight matching
        
    :param G: a weighted ILPGraph                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """
    
    # Create model
    m = Model("graphilp_max_weight_matching")
    
    # Add variables for edges and nodes
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.node_variables
    
    # Create constraints
    ## choosing an edge implies choosing both of its nodes
    for edge, edge_var in edges.items():
        m.addConstr(edge_var - nodes[edge[0]] <= 0)
        m.addConstr(edge_var - nodes[edge[1]] <= 0)

    ## at most one edge can be adjacent to each node
    for node in nodes:
        m.addConstr(gurobipy.quicksum([edge_var for edge, edge_var in edges.items() if edge[0]==node or edge[1]==node]) <= 1)     
        
    # set optimisation objective: maximum weight matching (sum of weights of chosen edges)
    m.setObjective( gurobipy.quicksum([edge_var * G.G.edges[edge]['weight'] for edge, edge_var in edges.items()]), GRB.MAXIMIZE)
    
    return m

def extractSolution(G, model):
    """ Get a list of the edges comprising the maximum weight matching
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for maximum weight matching
            
        :return: a list of edges comprising the maximum weight matching
    """
    matching = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]
    
    return matching

