from gurobipy import *


def createModel(G):    
    """ Create an ILP for the minimum edge dominating set problem            
    Arguments:            G -- an ILPGraph                    
    Returns:            a Gurobi model     
    """        
    # Create model    
    m = Model("graphilp_min_edge_dominating_set")        
    # Add variables for edges   
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edges = G.edge_variables
    # Create constraints    
    ## for every edge, at least one adjacent edge or the edge itself must be taken  
    for (u, v) in G.G.edges:
        adjacent_edges = list(G.G.edges(u)) + list(G.G.edges(v)) 
        filter_adj = list(set([t if t[0] < t[1]  else t[::-1] for t in adjacent_edges ]))
        m.addConstr(gurobipy.quicksum( [edges[(i,j)] for (i,j) in filter_adj] )  >= 1 )
    # set optimisation objective: minimize cardinality of the edge dominating set   
    m.setObjective( gurobipy.quicksum(edges), GRB.MINIMIZE)      

    return m

def extractSolution(G, model):    
    """ Get a list of edges comprising a edge dominating set           
    Arguments:            G     -- a ILPGraph            
    model -- a solved Gurobi model for minimum edge dominating set                   
    Returns:            a list of edges comprising a minimum edge dominating set    """    
    dominating_set = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]        
    
    return dominating_set