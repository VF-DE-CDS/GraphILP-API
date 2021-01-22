from gurobipy import *

def createModel(G, A, direction=GRB.MAXIMIZE):
    """ Create an ILP for maximum/minimum bipartite perfect matching
        
        Arguments:
            G -- a weighted bipartite ILPGraph
            A -- subset of the vertex set of G giving the bipartition (each edge has exactly one end in A)
            direction -- GRB.MAXIMIZE for maximum weight matching, GRB.MINIMIZE for minimum weight matching
            
        Returns:
            a Gurobi model
    """
    
    # Create model
    m = Model("graphilp_bipartite_perfect_matching")
    
    # Add variables for edges and nodes
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.G.nodes()
    
    # Create constraints
    ## for each u in A there is exactly one edge adjacent to it
    for u in A:
        m.addConstr(gurobipy.quicksum([edge_var for edge, edge_var in edges.items() if u in edge]) == 1)
    
    ## for each v in V setminus A there is exactly one edge adjacent to it
    for v in nodes:
        if v not in A:
            m.addConstr(gurobipy.quicksum([edge_var for edge, edge_var in edges.items() if v in edge]) == 1)
            
    # set optimisation objective: maximum/minimum weight matching (sum of weights of chosen edges)
    m.setObjective(gurobipy.quicksum([edge_var * G.G.edges[edge]['weight'] for edge, edge_var in edges.items()]), direction)
    
    return m

def extractSolution(G, model):
    """ Get a list of the edges comprising the miniumum/maximum weight perfect bipartite matching
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for minimum/maximum weight perfect bipartite matching
            
        Returns:
            a list of edges comprising the minimum/maximum weight perfect bipartite matching
    """
    if model.Status == GRB.INFEASIBLE:
        matching = []
    else:
        matching = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]
    
    return matching


