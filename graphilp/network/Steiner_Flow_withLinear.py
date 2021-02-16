# +
import networkx as nx
from gurobipy import *


def createModel(G, terminals = [1,2], weight = 'weight', root = 1):    
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
    n = len(G.G.nodes())
    Capacity = Terminals
    
    edges = G.G.edges()
    
    # create model
    m = Model("Steiner Tree - Flow Formulation")        
    
    # create reverse edge for every edge in the graph
    for edge in G.G.edges(data=True):
        if ((edge[1], edge[0]) in edges):
            continue
        else:
            G.G.add_edge(edge[1], edge[0], Cost = edge[2]['Cost'])
    
    # Create Neighbourhood of the Root
    Neighbourhood = []
    for edge in G.G.edges():
        if edge[0] == root:
            Neighbourhood.append(edge)

    print(Neighbourhood)
    # Edge variables y
    y = {}
    f = {}

    # Label variable x
    x = {}
    l = {}
    
    for edge in G.G.edges():
        # Variable that determiens whether edge is chosen
        y[edge] = m.addVar(vtype = GRB.BINARY, name = "y" + str(edge))
        
        # Variable the determines the flow amount on the edge
        f[edge] = m.addVar(name = "f" + str(edge), lb = 0, ub = Capacity)

    for node in G.G.nodes():
        # Label Variable of the Node
        l[node] = m.addVar(vtype = gurobipy.GRB.INTEGER, lb = 0, ub = n)

        # Decision Variable that specifies whether this node is chosen
        x[node] = m.addVar(vtype = gurobipy.GRB.BINARY)
    m.update()  

    # abbreviations
    edges = G.G.edges()
    nodes = G.G.nodes()
    
    # set objective: minimise the sum of the costs of edges selected for the solution
    m.setObjective(gurobipy.quicksum([y[edge] * G.G.edges[edge][weight] for edge in edges]), GRB.MINIMIZE)

    for edge in edges:
        # at most one direction per edge can be chosen
        # runtime can probably be greatly improved if iterating is done in a smarter way
        reverseEdge = edge[::-1]
        m.addConstr(y[edge] + y[reverseEdge] <= 1)
        
        # Maximum Capacity must not be exceeded for every edges
        m.addConstr(f[edge] <= y[edge] * Capacity)
        
        # Labeling constraints
        m.addConstr( n * y[reverseEdge] + l[edge[1]] - l[edge[0]] >= 1 - n*(1 - y[edge]))
        m.addConstr( n * y[edge] + l[edge[0]] - l[edge[1]] >= 1 - n*(1 - y[reverseEdge]))
        
        # If edge is chosen, both Nodes need to be chosen
        m.addConstr(2*y[edge] - x[edge[0]] -x[edge[1]] <= 0)

    # Flow conservation constraint
    for j in nodes:
        incomingEdges = []
        outgoingEdges = []
        # Searching for all incoming and outgoing Edges from and into the Node
        for i in nodes:
            if (i == j):
                continue
            if ((i, j) in edges):
                incomingEdges.append((i,j))
            if((j, i) in edges):
                outgoingEdges.append((j,i))
        # If a node that is not the Root, Source or a Terminal is found, no flow must be lost
        if j != root and (j not in terminals):
            m.addConstr(sum(f[edgeOut] for edgeOut in outgoingEdges) - sum(f[edgeIn] for edgeIn in incomingEdges) == 0)
        # Else if a terminal was found, it has to consume a flow of 1
        elif (j in terminals and j != root):
            m.addConstr(sum(f[edgeIn] for edgeIn in incomingEdges) - sum(f[edgeOut] for edgeOut in outgoingEdges)== 1)

    # Flow is started from Root node. Outgoing Flow has to be enough to fill all nodes
    m.addConstr(gurobipy.quicksum(f[edge] for edge in Neighbourhood) == Terminals - 1)   
    
    # Flow is started from Root node and must not be returned to Source Node
    for t in terminals:
        m.addConstr(x[t] == 1)
    
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


