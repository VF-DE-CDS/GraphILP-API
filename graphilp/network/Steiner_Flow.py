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

            \begin{align*}
            \min \sum_{(i,j) \in E} w_{ij} x_{ij}\\
            \text{s.t.} &&\\
            x_{ij} + x_{ji} \leq 1 && \text{(restrict edges to one direction)}\\
            x_r = 1 && \text{(require root to be chosen)}\\
            \sum x_i - \sum x_{ij} = 1 && \text{(enforce circle when graph is not connected)}\\
            2(x_{ij}+x_{ji}) - x_i - x_j \leq 0 && \text{(require nodes to be chosen when edge is chosen)}\\
            x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated nodes)}\\
            n x_{uv} + \ell_v - \ell_u \geq 1 - n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            n x_{vu} + \ell_u - \ell_v \geq 1 - n(1-x_{uv}) && \text{(enforce increasing labels)}\\
            \end{align*}

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
        G.G.add_edge(edge[1], edge[0], Cost = edge[2]['Cost'])
    
    # Edge variables y
    y = {}
    z = {}
    for edge in G.G.edges():
        y[edge] = m.addVar(vtype = gurobipy.GRB.BINARY, name = "y" + str(edge))
        z[edge] = m.addVar(vtype = gurobipy.GRB.INTEGER, name = "z" + str(edge))
    #G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))
    # Flow Variables z
    #G.setFlowVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.INTEGER, name = "z"))
    m.update()  

    # abbreviations
    edges = G.G.edges()
    nodes = G.G.nodes()
    edge2var = dict(zip(edges.keys(), edges.values()))
    
    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([y[edge] * 5 for edge in edges]), GRB.MINIMIZE)

    for edge in edges:
        # at most one direction per edge can be chosen
        # runtime can probably be greatly improved if iterating is done in a smarter way
        reverseEdge = edge[::-1]
        m.addConstr(y[edge] + y[reverseEdge] <= 1)
        # Maximum Capacity must not be exceeded for every edges
        m.addConstr(z[edge] <= y[edge] * Capacity)
    
    # All flow has to end in the Root
    m.addConstr(gurobipy.quicksum(z[edge] for edge in Neighbourhood) == Terminals)   

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
            m.addConstr(sum(z[edgeOut] for edgeOut in outgoingEdges) - sum(z[edgeIn] for edgeIn in incomingEdges) == 0)

    # Flow is started from Source node and must not be returned to Source Node
    for t in terminals:
        m.addConstr(z[0, t] == 1)
        m.addConstr(z[t, 0] == 0)
    print(m.computeIIS())
    m.optimize() 
    for edge in edges:
        if ((m.getVarByName("z"+str(edge))).X > 0.5):
            print(m.getVarByName("z"+str(edge)))
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


