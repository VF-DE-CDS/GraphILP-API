from gurobipy import *
import math


def createModel(G, direction=GRB.MAXIMIZE):    
    r""" Create an ILP for the minimum/maximum bisection problem
    
    :param G: an ILPGraph                    
    :param direction: GRB.MAXIMIZE for maximum weight matching, GRB.MINIMIZE for minimum weight matching
    
    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    
    ILP:
        .. math::
            :nowrap:
            
            \begin{align*}
            & \min / \max_{\{u,v\} \in E} \sum x_{u,v}\\
            & \text{s.t.} &\\
            & \sum_{v \in V} x_v \leq \lceil |V|/2 \rceil & \text{(lower bound size of one partition)}\\
            & \sum_{v \in V} x_v \geq \lfloor |V|/2 \rfloor & \text{(upper bound size of one partition)}\\
            & \forall \{u,v\} \in E: x_{u, v} \leq x_u + x_v & \text{(no edge between partitions)}\\
            & \forall \{u,v\} \in E: x_{u, v} \leq 2 - x_u - x_v & \text{(no edge between partitions)}\\
            \end{align*}    
    """        
    # Create model    
    m = Model("graphilp_bisection")  
    
    # Add variables for edges and nodes    
    G.setEdgeVars(m.addVars(G.G.edges(), vtype=gurobipy.GRB.BINARY))
    G.setNodeVars(m.addVars(G.G.nodes(), vtype=gurobipy.GRB.BINARY))
    m.update()

    edges = G.edge_variables
    nodes = G.node_variables
    
    number_nodes = len(G.G.nodes())
    bound_upper = math.ceil(number_nodes/2)
    bound_lower = math.floor(number_nodes/2)

    # Create constraints
    # balanced solutions are needed
    m.addConstr(gurobipy.quicksum(nodes) <= bound_upper)
    m.addConstr(gurobipy.quicksum(nodes) >= bound_lower)

    ## for every edge, the nodes must be separated    
    for (u, v) in G.G.edges():                
        m.addConstr(edges[(u, v)] <= nodes[v] + nodes[u])
        m.addConstr(edges[(u, v)] <= 2 - nodes[v] - nodes[u]) 
   
    # set optimisation objective: minimize/maximize the cardinality of the number of edges in the cut   
    m.setObjective(gurobipy.quicksum(edges), direction)   

    return m


def extractSolution(G, model):    
    """ Get a list of vertices comprising a minimum/maximum balanced cut of G 
    
    :param G: an ILPGraph            
    :param model: a solved Gurobi model for the minimum/maximum bisection problem  
    
    :return: a list of vertices comprising a minimum/maximum balanced cut of G
    """    
    cut_nodes = [node for node, node_var in G.node_variables.items() if node_var.X > 0.5]        
    
    return cut_nodes
