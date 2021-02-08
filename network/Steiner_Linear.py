# +
from gurobipy import *
import networkx as nx

def createModel(G, terminals, weight = 'weight', cycleBasis: bool = False, nodeColoring: bool = False):    
    """ Create an ILP for the linear Steiner Problem. The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    Arguments:            G -- an ILPGraph                    
    Returns:              a Gurobi model     
    """        
    # Create model
    m = Model("Steiner Tree")        
    
    n = G.G.number_of_nodes()

    # create edge variables
    for edge in G.G.edges():
        G.G.add_edge(*edge[::-1])

    G.setNodeVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))
    G.setLabelVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.INTEGER, lb = 1, ub = n))

    m.update()  

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    edge2var = dict(zip(edges.keys(), edges.values()))
    # create node variables
    # create node variables and node label variables
    # for node in node_list:
    #    m.addVar(vtype=gurobipy.GRB.BINARY, name="node_" + str(node))
    #    m.addVar(vtype=gurobipy.GRB.INTEGER, lb=1, ub=G.G.number_of_nodes(), name="label_" + str(node))

    
      

    m.setObjective(gurobipy.quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), GRB.MINIMIZE)
    
    # OLD
    # Enforce terminals
    # for t in terminals:
    #    m.addConstr(m.getVarByName("node_" + str(t)) == 1)

    # NEW
    # equality constraints for terminals (each terminal needs to be chosen, i.e. set it's value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)

    # OLD
    # restrict number of edges
    # m.addConstr(  gurobipy.quicksum([m.getVarByName("node_" + str(node)) for node in node_list])\
    #             - gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u,v) in edge_list])\
    #             - gurobipy.quicksum([m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u,v) in edge_list]) == 1)
    
    # NEW
    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(gurobipy.quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

    # OLD
    # at most one direction per edge can be chosen
    # for (u,v) in edge_list:
    #     m.addConstr(m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)) <= 1)
    

    # NEW, runtime can be greatly improved if iterating is done in a smarter way
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        rev_edge_var = edge2var.get(reverseEdge)
        if rev_edge_var != None:
            m.addConstr(edge_var + rev_edge_var <= 1)

    # 
    # OLD
    # if edge is chosen, both adjacent nodes need to be chosen
    # for (u, v) in edge_list:
    #    m.addConstr(  2 * (m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("edge_" + str(v) + "_" + str(u)))\
    #                - m.getVarByName("node_" + str(u))\
    #                - m.getVarByName("node_" + str(v)) <= 0 )

    # NEW
    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)



    # OLD
    # prohibit isolated vertices
    # for node in node_list:
    #    edge_vars = [m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edge_list if (node==u) or (node==v)]\
    #              + [m.getVarByName("edge_" + str(v) + "_" + str(u)) for (u, v) in edge_list if (node==u) or (node==v)]
    #    m.addConstr(m.getVarByName("node_" + str(node)) - gurobipy.quicksum(edge_vars) <= 0)
    
    # NEW
    # prohibit isolated vertices
    for node, node_var in nodes.items():
        edge_vars = []
        for edge, edge_var in edges.items():
            if (node == edge[0] or node == edge[1]):
                edge_vars.append(edge_var)
        m.addConstr(node_var - gurobipy.quicksum(edge_vars) <= 0)

    
    # Orientation and labeling constraint alternative
    # n = G.G.number_of_nodes()
    # for (u,v) in edge_list:
    #    m.addConstr(  n * m.getVarByName("edge_" + str(v) + "_" + str(u)) + m.getVarByName("label_" + str(v))\
    #                - m.getVarByName("label_" + str(u)) >= 1 - n*(1-m.getVarByName("edge_" + str(u) + "_" + str(v))))
    #    m.addConstr(  n * m.getVarByName("edge_" + str(u) + "_" + str(v)) + m.getVarByName("label_" + str(u))\
    #                - m.getVarByName("label_" + str(v)) >= 1 - n*(1-m.getVarByName("edge_" + str(v) + "_" + str(u))))
    
    # NEW
    # Orentation and labeling constraints 
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        edge_var_rev = edge2var.get(reverseEdge)
        if edge_var_rev != None:
            m.addConstr( n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr( n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))



    # OLD, completely deleted since at most one direction for each nodepair was constrained before   
    # allow only one arrow into each node
    # for node in node_list:
    #    edges =  [(u, v) for (u, v) in edge_list if v == node]
    #    edges += [(v, u) for (u, v) in edge_list if u == node]
    #    m.addConstr(gurobipy.quicksum([m.getVarByName("edge_" + str(u) + "_" + str(v)) for (u, v) in edges]) <= 1)
    
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
