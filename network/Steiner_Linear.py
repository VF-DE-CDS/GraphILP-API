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
    
    # Add variables for edges and nodes
    global node_list, edge_list, edge_dict, rev_edge_dict
    node_list = G.G.nodes()
    edge_list = G.G.edges()
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))

    # create node variables
    # create node variables and node label variables
    for node in node_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
        m.addVar(vtype=gurobipy.GRB.INTEGER, lb=1, ub=G.G.number_of_nodes(), name="label_" + str(node))

    # create edge variables
    for edge in edge_list:
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[0]) + "_" + str(edge[1]))
        m.addVar(vtype=gurobipy.GRB.BINARY, name="edge_" + str(edge[1]) + "_" + str(edge[0]))

    m.update()    

    m.setObjective(
        gurobipy.quicksum([G.G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list])\
        + gurobipy.quicksum([G.G.edges[u,v]['weight'] * m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list]),\
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
    n = G.G.number_of_nodes()
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

def extractSolution(G, model):
    """ Get the optimal tour in G 
    
        Arguments:
            G     -- a weighted ILPGraph
            model -- a solved Gurobi model for min/max Path asymmetric TSP 
            
        Returns:
            the edges of an optimal tour/path in G 
    """
    edge_list = G.G.edges()
    tst = set(edge_list)
    G.G.remove_edges_from([(u, v) for (u, v) in edge_list if (v, u) in tst])
    edge_list = list(G.G.edges())
    edge_dict = dict(enumerate(edge_list))
    rev_edge_dict = dict(zip(edge_dict.values(), edge_dict.keys()))
    
    solution = [(u,v) for (u,v) in G.G.edges if model.getVarByName("edge_" + str(u) + "_" + str(v)).X > 0.1]
    solution += [(v,u) for (u,v) in G.G.edges if model.getVarByName("edge_" + str(v) + "_" + str(u)).X > 0.1]
    
    print(solution)
    
    return solution
