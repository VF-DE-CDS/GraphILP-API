# +
from gurobipy import *
import networkx as nx

def createModel(G, terminals, root, weight = 'weight', minCapacity = 20):    
    r""" Create an ILP for the linear Steiner Problem with additional Flow Constraints. 
    Flow Constraints limit the maximum amount of FLow from a specified root to the Terminals.
    Each edge has a limit of flow it can transport, i.e. minCapacity. This flow can be extended to a larger amount, i.e. each edges Capacity.  
      
    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param minCapacity: Current amount of Capacity that exists on each edge

    :return: a Gurobi model

    ILP:
        .. math::
            :nowrap:

            \section{Sets}
                Edges \indent E = $\{(i,j) \in E : i \in V, j \in V, i \ne j\}$ \newline
                Nodes \indent V = $\{i\}$ \newline
                Terminals T = $\{i \in V :$ i is a terminal Node\} \newline
                Neighborhood O(i) = $\{(i, j) \in E : $ j is connected to i \}
            \section{Decision Variables}
                \begin{tabular}{l l}
                    $y_{i,j}$ & Binary variable whether edge (i, j) is chosen\\
                    $w_{i,j}$ & Binary variable whether edge (i, J) is expanded by a fibre connection\\
                    $f_{i,j}$ & Flow amount from i to j  \\
                    $x_{i}$ & Binary variable whether node i is chosen \\
                    $l_{i}$ & Label variables for the nodes to indicate "when" they where chosen \\
                \end{tabular}
            \newline
            \section{Objective Function}
                \begin{tabular}{l l}
                    Min z = $\sum_{i,j \in E} c_{i,j} \cdot y_{i,j}$ & Minimize costs of adding new edges \\
                \end{tabular}
            \section{Parameters}
                \begin{tabular}{l l}
                    $|T|$   &  Amount of Terminal Nodes in the Model \\
                    $Cap_{(i, j)}$ & Maximum Capacity of edge by supplying it with Fibre (i,j) \\
                    $b_i$ & Demand of node i\\
                    $CurCap_{(i,j)}$ & Current capacity on edge (i,j) \\
                \end{tabular}\newline
            \section{Constraints}
                \begin{tabular}{l l }
                    Only one direction of Edges between two Nodes can be chosen at once\\
                        \indent $x_{i,j} + x_{j, i} \leq 1$ & $\forall (i,j) \in E$\\
                    Prohibit isolated nodes \\
                        \indent $x_{i}-\sum_{u=i \vee v=i}x_{uv} \leq 0$ & $\forall i \in V$ \\
                    Enforce increasing labels \\
                        \indent $ n \ast x_{(i,j)} + \ell_j - \ell_i \geq 1 - n \ast (1-x_{(j,i)})$ & $\forall (i,j) \in E$ \\    
                        \indent $ n \ast x_{(j,i)} + \ell_i - \ell_j \geq 1 - n \ast (1-x_{(i,j)})$ & $\forall (i,j) \in E$ \\
                    All Flow has to come from the Root and has to end in each of the Terminals\\
                        \indent$ \sum_{j \in O(r)} f_{i, j} = \sum_{i} b_i$ & \\
                    Flow conservation constraint \\
                        \indent $\sum_{i, j \in E} f_{i, j} - \sum_{j, k \in E} f_{j, k} = 0$ & $\forall j \in V \backslash T$ \\
                        \indent $\sum_{i, j \in E} f_{i, j} - \sum_{j, k \in E} f_{j, k} = b_i$ & $\forall j \in T \subseteq V$ \\
                    There can only be flow when the edge is activated (but maximum Capacity) \\
                        \indent $f_{i, j} \leq y_{i, j} * Cap_{(i, j)} + CurCap_{(i,j)}$ & $\forall (i,j) \in E$ \\
                    Chose nodes when edge is chosen \\
                        \indent $2(x_{ij}+x_{ji}) - x_i - x_j \leq 0 $ & $\forall (i,j) \in E$\\
                    All Terminals must be chosen \\
                        \indent $x_{t} = 1$ & $\forall t \in T \subseteq V$ \\
                    Variable Domains \\
                            
                        \indent $y_{i, j} \in \{0, 1\}$ & $\forall (i, j) \in E$ \\
                        \indent $f_{i, j} \geq 0$ & $\forall (i, j) \in E$ \\
            \end{tabular}

    """        
    
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)

    # create model
    m = Model("Steiner Tree")    
    totLoad = 0
    for node in G.G.nodes(data=True):
        if (node[0] == root):
            continue
        totLoad += G.G.nodes[node[0]]['Weight']

    n = G.G.number_of_nodes()

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        reverseEdge = edge[::-1]
        if (reverseEdge not in G.G.edges()):
            G.G.add_edge(*edge[::-1])
    
    # Create Neighbourhood of the Root
    fromRoot = []
    inRoot = []
    for edge in G.G.edges():
        if edge[0] == root:
            fromRoot.append(edge)
            inRoot.append(edge[::-1])

    G.setNodeVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.BINARY))
    G.setEdgeVars(m.addVars(G.G.edges(), vtype = gurobipy.GRB.BINARY))

    G.setLabelVars(m.addVars(G.G.nodes(), vtype = gurobipy.GRB.INTEGER, lb = 1, ub = n))
    G.flow_variables = m.addVars(G.G.edges(), vtype = gurobipy.GRB.INTEGER, lb = 0)
    
    m.update()  

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    flow = G.flow_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(gurobipy.quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]), GRB.MINIMIZE)
    
    # equality constraints for terminals (each terminal needs to be chosen, i.e., set its value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(gurobipy.quicksum(nodes.values()) - gurobipy.quicksum(edges.values()) == 1)

    # at most one direction per edge can be chosen
    # runtime can probably be greatly improved if iterating is done in a smarter way
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        rev_edge_var = edge2var.get(reverseEdge)
        m.addConstr(edge_var + rev_edge_var <= 1)

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
        if edge_var_rev != None:
            m.addConstr( n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr( n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

        
    # Flow is started from Root node. Outgoing Flow has to be enough to fill all nodes
    m.addConstr(gurobipy.quicksum(flow[edge] for edge in fromRoot) == totLoad)   
    
    
    # Flow amount must not exceed edge's capacity. If the edge is not chosen, the flow has to always be 0.
    for edge in G.G.edges(data=True):
        m.addConstr(flow[(edge[0],edge[1])] <= edges[(edge[0], edge[1])] * edge[2]['Capacity'] + minCapacity)
    
    # No flow is allowed to the root
    for edge in inRoot:
        m.addConstr(flow[edge] == 0)
    
    # Flow conservation constraints
    for node in G.G.nodes(data=True):
        # Getting all Edges that leave away from the Node, i.e. the Node is the startpoint of the edge
        outgoingEdges = [edge for edge in G.G.edges() if edge[0] == node[0]]
        # And all incoming edges, i.e. Node is the endpoint of the edge
        incomingEdges = [edge for edge in G.G.edges() if edge[1] == node[0]]
        
        if node[0] != root:
            m.addConstr(sum(flow[edgeIn] for edgeIn in incomingEdges) - sum(flow[edgeOut] for edgeOut in outgoingEdges) == node[1]['Weight'])
    
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


