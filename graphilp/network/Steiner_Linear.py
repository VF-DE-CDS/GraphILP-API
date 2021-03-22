# +
from gurobipy import *
import networkx as nx

def createModel(G, terminals, weight = 'weight', warmstart=[], lower_bound=None):    
    r""" Create an ILP for the linear Steiner Problem. 
    
    This formulation enforces a cycle in the solution if it is not connected.
    Cycles are then forbidden by enforcing an increasing labelling along the edges of the solution.
    To this end, the formulation is working with a directed graph internally.
    
    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param warmstart: a list of edges forming a tree in G connecting all terminals
    :param lower_bound: give a known lower bound to the solution length

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`n = |V|` be the number of vertices in G and :math:`T` the set of terminals.
        Further, let :math:`\overrightarrow{E} := \{(u, v), (v, u) \mid \{u, v\} \in E\}` 
        be the directed edge set used in the internal representation.
    
        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{(uvj) \in E} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall \{u,v\} \in E: x_{uv} + x_{vu} \leq 1 && \text{(restrict edges to one direction)}\\
            \forall t \in T: x_t = 1 && \text{(require terminals to be chosen)}\\
            \sum_{v \in V} x_v - \sum_{(u, v) \in \overrightarrow{E}} x_{uv} = 1 && \text{(enforce cycle when graph is not connected)}\\
            \forall \{u,v\}\in E: 2(x_{uv}+x_{vu}) - x_u - x_v \leq 0 && \text{(require nodes to be chosen when edge is chosen)}\\
            \forall i \in V: x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated nodes)}\\
            \forall \{u,v\}\in E: n x_{uv} + \ell_v - \ell_u \geq 1 - n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: n x_{vu} + \ell_u - \ell_v \geq 1 - n(1-x_{uv}) && \text{(enforce increasing labels)}\\
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

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        G.G.add_edge(*edge[::-1])
        
    # create model
    m = Model("Steiner Tree")        
    
    n = G.G.number_of_nodes()

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
    m.setObjective(quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), GRB.MINIMIZE)
    
    # equality constraints for terminals (each terminal needs to be chosen, i.e., set its value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

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
        m.addConstr(node_var - quicksum(edge_vars) <= 0)

    
    # labeling constraints: enforce increasing labels in edge direction of selected edges 
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        edge_var_rev = edge2var.get(reverseEdge)
        if edge_var_rev != None:
            m.addConstr( n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr( n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))

    # allow only one arrow into each node
    for node in nodes:
        constraint_edges =  [(u, v) for (u, v) in edges.keys() if v == node]
        m.addConstr(quicksum([edges[e] for e in constraint_edges]) <= 1)

    # set lower bound
    if lower_bound:
        m.addConstr(quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]) >= lower_bound)

    m.update()
        
    # set warmstart
    if len(warmstart) > 0:
        
        # Initialise warmstart by excluding all edges and vertices from solution:
        for edge_var in edges.values():
            edge_var.Start = 0
            
        for node_var in nodes.values():
            node_var.Start = 0

        for label_var in labels.values():
            label_var.Start = 1
            
        # Include all edges and vertices from the warmstart in the solution
        # and set vertex labels:
        start_node = warmstart[0][0]
        
        warmstart_tree = nx.Graph()
        warmstart_tree.add_edges_from(warmstart)
        
        label = {start_node: 1}
        labels[start_node].Start = 1
        bfs = nx.bfs_edges(warmstart_tree, start_node)
        
        for e in bfs:
            label[e[1]] = label[e[0]] + 1
            labels[e[1]].Start = label[e[1]]
            
            edges[e].Start = 1
                
            nodes[e[0]].Start = 1
            nodes[e[1]].Start = 1
        
    m.update()
        
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
