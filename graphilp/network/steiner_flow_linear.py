from gurobipy import Model, GRB, quicksum
import networkx as nx

def create_model(G, terminals, root, weight='weight', minCapacity=20):
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

            \begin{align*}
            \forall (u,v) \in E: x_{uv} + x_{vu} \leq 1 \in E && \text{(at most one direction per edges)}\\
            \forall i \in V: x_{i}-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(prohibit isolated nodes)}\\
            \forall (u,v) \in E: n x_{(u,v)} + \ell_v - \ell_u \geq 1 - n (1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall (u,v) \in E: n x_{(v,u)} + \ell_u - \ell_v \geq 1 - n (1-x_{uv}) && \text{(enforce increasing labels)}\\
            \sum_{j \in O(r)} f_{i, j} = \sum_{i} b_i && \text{(flow starts at root and ends at terminals)} \\
            \forall j \in V \backslash T: \sum_{i, j \in E} f_{i, j} - \sum_{j, k \in E} f_{j, k} = 0 
            && \text{(flow conservation)}\\
            \forall j \in T: \sum_{i, j \in E} f_{i, j} - \sum_{j, k \in E} f_{j, k} = b_i
            && \text{(flow conservation)}\\
            \forall (i,j) \in E: f_{ij} \leq y_{ij} Cap_{ij} + CurCap_{ij} &&
            \text{(there can only be flow when the edge is activated (but maximum Capacity))} \\
            \forall (i,j) \in E: 2(x_{ij}+x_{ji}) - x_i - x_j \leq 0 &&
            \text{(choose nodes when edge is chosen)} \\   
            \forall t \in T: x_{t} = 1 && \text{(all terminals must be chosen)}\\
            \end{align*}
    """        
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)

    # create model
    m = Model("Steiner Tree")
    tot_load = 0
    for node in G.G.nodes(data=True):
        if (node[0] == root):
            continue
        tot_load += G.G.nodes[node[0]]['Weight']

    n = G.G.number_of_nodes()

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        reverseEdge = edge[::-1]
        if (reverseEdge not in G.G.edges()):
            G.G.add_edge(*edge[::-1])

    # Create Neighbourhood of the Root
    from_root = []
    in_root = []
    for edge in G.G.edges():
        if edge[0] == root:
            from_root.append(edge)
            in_root.append(edge[::-1])

    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))

    G.set_label_vars(m.addVars(G.G.nodes(), vtype=GRB.INTEGER, lb=1, ub=n))
    G.flow_variables = m.addVars(G.G.edges(), vtype=GRB.INTEGER, lb=0)

    m.update()

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    flow = G.flow_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]), GRB.MINIMIZE)

    # equality constraints for terminals (each terminal needs to be chosen, i.e., set its value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(quicksum(nodes.values()) - quicksum(edges.values()) == 1)

    # at most one direction per edge can be chosen
    # runtime can probably be greatly improved if iterating is done in a smarter way
    for edge, edge_var in edges.items():
        reverse_edge = edge[::-1]
        rev_edge_var = edge2var.get(reverse_edge)
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
        m.addConstr(node_var - quicksum(edge_vars) <= 0)

    # labeling constraints: enforce increasing labels in edge direction of selected edges
    for edge, edge_var in edges.items():
        reverseEdge = edge[::-1]
        edge_var_rev = edge2var.get(reverseEdge)
        if edge_var_rev is not None:
            m.addConstr(n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr(n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

    # Flow is started from Root node. Outgoing Flow has to be enough to fill all nodes
    m.addConstr(quicksum(flow[edge] for edge in from_root) == tot_load)


    # Flow amount must not exceed edge's capacity. If the edge is not chosen, the flow has to always be 0.
    for edge in G.G.edges(data=True):
        m.addConstr(flow[(edge[0], edge[1])] <= edges[(edge[0], edge[1])] * edge[2]['Capacity'] + minCapacity)

    # No flow is allowed to the root
    for edge in in_root:
        m.addConstr(flow[edge] == 0)

    # Flow conservation constraints
    for node in G.G.nodes(data=True):
        # Getting all Edges that leave away from the Node, i.e. the Node is the startpoint of the edge
        outgoing_edges = [edge for edge in G.G.edges() if edge[0] == node[0]]
        # And all incoming edges, i.e. Node is the endpoint of the edge
        incoming_edges = [edge for edge in G.G.edges() if edge[1] == node[0]]

        if node[0] != root:
            m.addConstr(sum(flow[edgeIn] for edgeIn in incoming_edges) - sum(flow[edge_out] for edge_out in outgoing_edges) == node[1]['Weight'])

    return m


def extract_solution(G, model):
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
