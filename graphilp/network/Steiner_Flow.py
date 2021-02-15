# +
from gurobipy import *
import networkx as nx

def createModel(G, terminals = [1,2], weight = 'Cost', root = 1):    
    r""" Create an ILP for the linear Steiner Problem. 
    
    The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    
    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost

    :return: a Gurobi model

    ILP:
        .. math::
            :nowrap:


    Example:
            .. list-table:: 
               :widths: 50 50
               :header-rows: 0

               * - .. image:: example_steiner.png
                 - `Steiner trees <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/SteinerTreesOnStreetmap.ipynb>`_

                   Find the shortest tree connecting a given set of nodes in a graph.
    """        
    
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)
    
    Terminals = len(terminals)
    Capacity = 2000
    
    edges = G.G.edges()

    # Create Neighbourhood of the Root
    Neighbourhood = []
    for edge in G.G.edges():
        if edge[0] == root or edge[1] == root:
            Neighbourhood.append(edge)
    
    # create model
    m = Model("Steiner Tree - Flow Formulation")        
    source = 0
    
    for terminal in terminals:
        G.G.add_edge(source, terminal, Cost = 0)
    
    # create reverse edge for every edge in the graph
    for edge in G.G.edges(data=True):
        if ((edge[1], edge[0]) in edges):
            continue
        else:
            G.G.add_edge(edge[1], edge[0], Cost = edge[2]['Cost'])
    
    # Edge variables y
    y = {}
    f = {}
    for edge in G.G.edges():
        y[edge] = m.addVar(vtype = gurobipy.GRB.BINARY, name = "y" + str(edge))
        f[edge] = m.addVar(name = "f" + str(edge), lb = 0, ub = Capacity)
    #G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))
    # Flow Variables z
    #G.setFlowVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.INTEGER, name = "z"))
    m.update()  

    # abbreviations
    edges = G.G.edges()
    nodes = G.G.nodes()
    edge2var = dict(zip(edges.keys(), edges.values()))
    
    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([y[edge] * 1 for edge in edges]), GRB.MINIMIZE)

    for edge in edges:
        # at most one direction per edge can be chosen
        # runtime can probably be greatly improved if iterating is done in a smarter way
        reverseEdge = edge[::-1]
        m.addConstr(y[edge] + y[reverseEdge] <= 1)
        # Maximum Capacity must not be exceeded for every edges
        m.addConstr(f[edge] <= y[edge] * Capacity)
    
    # All flow has to end in the Root
    m.addConstr(gurobipy.quicksum(f[edge] for edge in Neighbourhood) == Terminals - 1)   

    # Flow conservation constraint
    for j in nodes:
        incomingEdges = []
        outgoingEdges = []
        for i in nodes:
            if (i == j):
                continue
            if ((i, j) in edges):
                incomingEdges.append((i,j))
            if((j, i) in edges):
                outgoingEdges.append((j,i))
        if j != root and j != 0:
            m.addConstr(sum(f[edgeOut] for edgeOut in outgoingEdges) - sum(f[edgeIn] for edgeIn in incomingEdges) == 0)

    # Flow is started from Source node and must not be returned to Source Node
    for t in terminals:
        if t == root:
            m.addConstr(f[0, t] == 0)
            m.addConstr(f[t, 0] == 0)
            continue
        m.addConstr(f[0, t] == 1)
        m.addConstr(f[t, 0] == 0)
        m.addConstr(y[0, t] == 1)
        m.addConstr(y[t, 0] == 0)
    #print(m.computeIIS())
    m.optimize() 
    for edge in edges:
        if ((m.getVarByName("f"+str(edge))).X > 0.5):
            print(m.getVarByName("f"+str(edge)))
    return m

def extractSolution(G, model):
    r""" Get the optimal Steiner tree in G 
    
        :param G: a weighted ILPGraph
        :param model: a solved Gurobi model for the minimum Steiner tree problem
            
        :return: the edges of an optimal Steiner tree connecting all terminals in G
    """
    solution = []
    for edge, edge_var in G.edge_variables.items():
        if edge_var.X > 0.5:
            solution.append(edge)
    
    return solution
# -


