from gurobipy import *
from graphilp.covering import warmstart_vertex_covering as ws


def createModel(G, warmstart:bool = False):    
    """ Create an ILP for the minimum vertex cover problem
    
    :param G: an unweighted ILPGraph                    
    :param warmstart: choose whether to use a warmstart
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    """        
   # Create model    
    m = Model("graphilp_min_vertex_cover")    
    warmstartNodes = set()    
    # Add variables for edges and nodes    
    #if (warmstart == True):
    #    wsNodesHeur = ws.maximalMatching(G)
    #    wsNodesApprox = ws.createApproximation(G)
    #    print("Approx Nodes : ", len(wsNodesApprox))
    #    print("Heuristic Nodes: ",  len(wsNodesApprox)) 
    #    if (len(wsNodesHeur) < len(wsNodesApprox)):
    #        warmstartNodes = wsNodesHeur
    #        print("Chose Heuristic Warmstart")
    #    else:
    #        warmstartNodes = wsNodesApprox
    #        print("Chose Aprrox Warmstart")
    #warmstartNodes = ws.createApproximation(G)
    print("Heuristic done")    
    node_list = list(G.G.nodes())
    x = m.addVars(G.G.nodes(), vtype = GRB.BINARY)
    for i in node_list:
        if(i in warmstartNodes):
            x[i].Start = 1
    print("Start Nodes Set")
    m.update()            

    m.setObjective(sum(x[i] for i in node_list), GRB.MINIMIZE)
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges():            
        m.addConstr(x[int(u)] + x[int(v)] >= 1 )    
    
    m.optimize()
    return x

def extractSolution(G, model):    
    """ Get a list of vertices comprising a vertex cover  
    
    :param G: an ILPGraph            
    :param model: a solved Gurobi model for minimum vertex cover                    
    
    :return: a list of vertices comprising a minimum vertex cover
    """    
    vertex_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return vertex_nodes

def createModelWeighted(G):
    """ Create an ILP for the minimum vertex cover problem 
    
    :param G: a weighted ILPGraph   
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_    
    """        
    # Create model    
    m = Model("graphilp_min_vertex_cover")        
    # Add variables for edges and nodes    
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))    
    node_list = G.G.nodes()
    weights = []
    for node in node_list(data=True):
        weights.append(node[1]['prize'])
    m.update()    
    nodes = G.node_variables        
    # Create constraints    
    ## for every edge, at least one vertex must be in a vertex cover of G    
    for (u, v) in G.G.edges:                
        m.addConstr(nodes[u] + nodes[v] >= 1 )    
    # set optimisation objective: minimize cardinality of the vertex cover   
    m.setObjective( gurobipy.quicksum(nodes*weights), GRB.MINIMIZE)      

    return m
