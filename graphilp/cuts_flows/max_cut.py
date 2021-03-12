from gurobipy import *


def createModel(G, weight='weight', direction=GRB.MAXIMIZE):    
    r""" Create an ILP for the minimum/maximum weight cut problem
    
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param weight: name of the weight parameter in the edge dictionary of the graph
    :param direction: GRB.MAXIMIZE for maximum weight cut, GRB.MINIMIZE for minimum weight cut
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP: 
        .. math::
            :nowrap:

            \begin{align*}
            \min/\max \sum_{(u,v) \in E} w_{uv}x_{uv}\\
            \text{s.t.} &&\\
            \forall (u,v) \in E: x_{uv} & \leq x_u + x_v & \text{(for every edge, the nodes must be separated )}\\
            \forall (u,v) \in E: x_{uv} & \leq 2 - x_u - x_v & \text{(for every edge, the nodes must be separated )}\\
            \end{align*}

    """        
    # Create model    
    m = Model("graphilp_max_cut")     
    
    # Add variables for edges and nodes    
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY )) 
    m.update()    
    
    nodes = G.node_variables  
    edges = G.edge_variables
    
    # Create constraints    
    ## for every edge, the nodes must be separated    
    for (u, v) in G.G.edges:                
        m.addConstr( edges[(u, v)]  <= nodes[v] +nodes[u] )
        m.addConstr( edges[(u, v)] <= 2 - nodes[v] - nodes[u] ) 
        
    # set optimisation objective: maximize the total weight of edges in the cut      
    m.setObjective(quicksum([G.G.edges[edge].get(weight, 1) * edge_var for edge, edge_var in edges.items()]), 
                   direction)   

    return m


def extractSolution(G, model):    
    """ Get a list of vertices comprising a maximum cut of G   
    
    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`            
    :param model: a solved Gurobi model for min/max weight cut                    
    
    :return: a list of vertices comprising a minimum/maximum weight cut of G
    """    
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return cut_nodes
