from gurobipy import *


def createModel(G):    
    r""" Create an ILP for the minimum dominating set problem 
    
    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`                    
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
        .. math::
            :nowrap:
    
            \begin{align*}
            \min \sum_{v\in V}~x_v\\
            \text{s.t.}&&\\
            \forall v \in V:& \sum_{a\in \bigcup_{v\in e} e  }  x_a \geq 1 & \text{(each node is covered by a neighbour)}  
            \end{align*} 
    """        
    # Create model    
    m = Model("graphilp_min_dominating_set")     
    
    # Add variables for edges   
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))    
    m.update()
    
    nodes = G.node_variables
    # Create constraints    
    ## for every node, at least one adjacent node or the node itself must be taken  
    for u in G.G.nodes:
        m.addConstr(gurobipy.quicksum( [nodes[n] for n in G.G.neighbors(u)] ) + nodes[u]  >= 1)
        
    # set optimisation objective: minimize the cardinality of the dominating set   
    m.setObjective( gurobipy.quicksum(nodes), GRB.MINIMIZE)      

    return m

def extractSolution(G, model):    
    """ Get a list of edges comprising a dominating set  
    
    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`           
    :param model: a solved Gurobi model for minimum dominating set                   
    
    :return: a list of nodes comprising a minimum dominating set
    """    
    dominating_set = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return dominating_set
