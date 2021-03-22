# +
from gurobipy import *
import networkx as nx

def createModel(G, terminals, weight = 'weight', cycleBasis: bool = False, nodeColoring: bool = False, root = None):    
    r""" Create an ILP for the linear Steiner Problem. 
    
    The model can be seen in Paper Chapter 3.0. This model
    doesn't implement tightened labels.
    
    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

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

               * - .. image:: images/example_steiner.png
                 - `Steiner trees <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/SteinerTreesOnStreetmap.ipynb>`_

                   Find the shortest tree connecting a given set of nodes in a graph.
    """        
    
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)
        
    # create model
    m = Model("Steiner Tree")        
    
    n = G.G.number_of_nodes()

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        G.G.add_edge(*edge[::-1])

    # If no root is specified, set it to be the first terminal in the terminals list
    if (root == None):
        root = terminals[0]

    G.setNodeVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))

    # node label variables used to avoid cycles 
    G.setLabelVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.INTEGER, lb = 1, ub = n))

    m.update()  

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), GRB.MINIMIZE)
    
    # Each terminal and especially the root has to be chosen. 
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)
        elif node == root:
            # root needs to be chosen
            m.addConstr(node_var == 1)
            # Label of the root needs to be set to 1
            m.addConstr(labels[node] == 1)
            print(root)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(gurobipy.quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

    # at most one direction per edge can be chosen
    # runtime can probably be greatly improved if iterating is done in a smarter way
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        rev_edge_var = edge2var.get(reverseEdge)
        if rev_edge_var != None:
            m.addConstr(edge_var + rev_edge_var <= 1)

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

    # prohibit isolated vertices
    for node, node_var in nodes.items():
        edge_vars = []
        for edge, edge_var in edges.items():
            # If the node is startpoint or endpoint of the edge, add the edge
            # to the array of edge variables
            # Since the edges variable containt both directions, we can write this much short than
            # in the previous formulation
            if (node == edge[0] or node == edge[1]):
                edge_vars.append(edge_var)
        m.addConstr(node_var - gurobipy.quicksum(edge_vars) <= 0)

    
    # labeling constraints: enforce increasing labels in edge direction of selected edges 
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        edge_var_rev = edge2var.get(reverseEdge)
        u = edge[0]
        v = edge[1]
        if edge_var_rev != None:
            m.addConstr( labels[v] - 2 * n * edge_var_rev <= labels[u] + 1 + 2*n*(1 - edge_var))
            m.addConstr( labels[u] + 1 <= 2*n*edge_var_rev + labels[v] + 2*n*(1 - edge_var))
            m.addConstr( labels[u] - 2*n*edge_var <= labels[v] + 1 + 2*n*(1 - edge_var_rev))
            m.addConstr( labels[v] + 1 <= 2*n*edge_var + labels[u] + 2*n*(1 - edge_var_rev))
            
    # allow only one arrow into each node
    for node in nodes:
        constraint_edges =  [(u, v) for (u, v) in edges.keys() if v == node]
        m.addConstr(gurobipy.quicksum([edges[e] for e in constraint_edges]) <= 1)
    
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
