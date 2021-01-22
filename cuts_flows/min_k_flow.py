from gurobipy import *

def createModel(G):
    """ Create an ILP for the minimum k-flow problem (https://en.wikipedia.org/wiki/Nowhere-zero_flow)
        
        Arguments:
            G -- a weighted ILPGraph
            
        Returns:
            a Gurobi model 
    """
    
    # Create model
    m = Model("graphilp_min_k_flow")
    
    # add variables for flow values on edges
    edge_vars = m.addVars(G.G.edges(), lb = -G.G.number_of_edges(), ub = G.G.number_of_edges(), vtype=gurobipy.GRB.INTEGER)
    G.setEdgeVars(edge_vars)
    
    # add helper variables indicating whether flow on an edge is positive or negative
    sign_vars = m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY)
    
    # add target variable k bounding the flow
    k = m.addVar(vtype=gurobipy.GRB.INTEGER)
    
    G.sign_variables = sign_vars
    G.k = k
    
    m.update()

    # Create constraints

    # flow condition
    for node in G.G.nodes():
        m.addConstr(gurobipy.quicksum( [edge_vars[e] for e in G.G.edges() if e[0] == node]\
                                     + [-edge_vars[e] for e in G.G.edges() if e[1] == node] ) == 0)

    # flow bounded by k
    for edge, edge_var in edge_vars.items():
        m.addConstr(edge_var - k <= -1)
        m.addConstr(edge_var + k >= 1)

    # nowhere zero
    M = 2 * G.G.number_of_edges()

    for edge in G.G.edges():
        m.addConstr(M * sign_vars[edge] + edge_vars[edge] >= 1)
        m.addConstr(M * (1-sign_vars[edge]) - edge_vars[edge] >= 1)    

    # set optimisation objective: find the smallest k such that there is a nowhere-zero k-bounded flow 
    m.setObjective(k, GRB.MINIMIZE)
    
    return m

def extractSolution(G, model):
    """ Get the flow bound and a dictionary of edges weights realising a flow
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for minimum k-flow
            
        Returns:
            the minimal flow bound k and a dictionary of edges weights realising a flow
    """
    edge_vars = G.edge_variables
    
    weights = [      (edge, edge_var.X) if edge_var.X > 0 \
                else ((edge[1], edge[0]), -edge_var.X)\
                for edge, edge_var in edge_vars.items()]
    
    return G.k.X, dict(weights)



