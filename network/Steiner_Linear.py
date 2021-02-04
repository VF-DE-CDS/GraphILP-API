# +
from gurobipy import *
import networkx as nx

node_list = None
edge_list = None
edge_dict = None
rev_edge_dict = None

def createModel(G, terminals, cycleBasis: bool = False, nodeColoring: bool = False):    
    """ Create an ILP for the linear Steiner Problem. The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    Arguments:            G -- an ILPGraph                    
    Returns:              a Gurobi model     
    """        
    # Create model
    m = Model("Steiner Tree")        
    m.Params.threads = 3
    # Add variables for edges and nodes
    global node_list, edge_list, edge_dict, rev_edge_dict
    node_list = G.nodes
    edge_list = G.edges
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))

    # create node variables
    # create node variables and node label variables
    for node in node_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
        m.addVar(vtype=gurobipy.GRB.INTEGER, lb=1, ub=G.number_of_nodes(), name="label_" + str(node))

    # create edge variables
    for edge in edge_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[0]) + "_" + str(edge[1]))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[1]) + "_" + str(edge[0]))

    m.update()    

    m.setObjective(
        gurobipy.quicksum([G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list])\
        + gurobipy.quicksum([G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list]),\
        GRB.MINIMIZE)

    # Enforce terminals
    for t in terminals:
        m.addConstr(m.getVarByName("node_" + str(t)) == 1)

    # restrict number of edges
    m.addConstr(  gurobipy.quicksum([m.getVarByName("node_" + str(node)) for node in node_list])\
                - gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u,v) in edge_list])\
                - gurobipy.quicksum([m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u,v) in edge_list]) == 1)
    
    # at most one direction per edge can be chosen
    for (u,v) in edge_list:
        m.addConstr(m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)) <= 1)
    
    # if edge is chosen, both adjacent nodes need to be chosen
    for (u, v) in edge_list:
        m.addConstr(  2 * (m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)))\
                    - m.getVarByName("node_" + str(u))\
                    - m.getVarByName("node_" + str(v)) <= 0 )

    # prohibit isolated vertices
    for node in node_list:
        edge_vars = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if (node==u) or (node==v)]\
                  + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if (node==u) or (node==v)]
        m.addConstr(m.getVarByName("node_" + str(node)) - gurobipy.quicksum(edge_vars) <= 0)
    
    
    # Orientation and labeling constraint alternative
    n = G.number_of_nodes()
    for (u,v) in edge_list:
        m.addConstr(  n * m.getVarByName("edge_" + str(v) + "_" + str(u)) + m.getVarByName("label_" + str(v))\
                    - m.getVarByName("label_" + str(u)) >= 1 - n*(1-m.getVarByName("edge_" + str(u) + "_" + str(v))))
        m.addConstr(  n * m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("label_" + str(u))\
                    - m.getVarByName("label_" + str(v)) >= 1 - n*(1-m.getVarByName("edge_" + str(v) + "_" + str(u))))
        
    # allow only one arrow into each node
    for node in node_list:
        edges =  [(u, v) for (u, v) in edge_list if v == node]
        edges += [(v, u) for (u, v) in edge_list if u == node]
        m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edges]) <= 1)
    
    return m
