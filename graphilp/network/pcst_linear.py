from gurobipy import Model, GRB, quicksum
import networkx as nx


def create_model(G, forced_terminals=[], weight='weight', prize='prize'):
    r""" Create an ILP for the Prize Collecting Steiner Tree Problem.

    This formulation enforces a cycle in the solution if it is not connected.
    Cycles are then forbidden by enforcing an increasing labelling along the edges of the solution.
    To this end, the formulation is working with a directed graph internally.

    :param G: an ILPGraph
    :param forced_terminals: list of terminals that have to be connected
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param prize: name of the argument in the node dictionary of the graph used to store node prize values

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`n` be the number of vertices in the graph and  :math:`T_f` be the set of forced terminals required to be part of the solution.
        Further, let :math:`p_v` be the prize associated with each vertex :math:`v` and
        :math:`\overrightarrow{E} := \{(u, v), (v, u) \mid \{u, v\} \in E\}`
        be the directed edge set used in the internal representation.

        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{v \in V} p_v x_v- \sum_{(u,v) \in E} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall \{u,v\}\in E: x_{uv} + x_{vu} \leq 1 && \text{(restrict edges to one direction)}\\
            \forall t \in T_f: x_t = 1 && \text{(require forced terminals}\\
            && \text{to be chosen)}\\
            \sum_{v\in V} x_v - \sum_{(u,v) \in \overrightarrow{E}} x_{uv} = 1 && \text{(enforce circle when graph}\\
            && \text{is not connected)}\\
            \forall \{u,v\}\in E: 2(x_{uv}+x_{vu}) - x_u - x_v \leq 0 && \text{(require vertices to be chosen}\\
            && \text{when edge is chosen)}\\
            \forall i \in V: x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated vertices)}\\
            \forall \{u,v\}\in E: n x_{uv} + \ell_v - \ell_u \geq 1 - n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: n x_{vu} + \ell_u - \ell_v \geq 1 - n(1-x_{uv}) && \text{(enforce increasing labels)}\\
            \end{align*}
    """
    # ensure that input is a directed graph
    if type(G.G) != nx.classes.digraph.DiGraph:
        G.G = nx.DiGraph(G.G)

    # create model
    m = Model("graphilp_pcst")

    n = G.G.number_of_nodes()

    # create reverse edge for every edge in the graph
    for edge in G.G.edges():
        G.G.add_edge(*edge[::-1])

    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))

    # node label variables used to avoid cycles
    G.setLabelVars(m.addVars(G.G.nodes(), vtype=GRB.INTEGER, lb=1, ub=n))

    m.update()

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([G.G.nodes[node].get(prize, 0) * node_var for node, node_var in nodes.items()])
                   - quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]),
                   GRB.MAXIMIZE)

    # equality constraints for forced terminals (each terminal needs to be chosen, i.e., set its value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in forced_terminals:
            m.addConstr(node_var == 1)

    # restrict number of edges, at max one edge between each pair of nodes
    m.addConstr(quicksum(nodes.values()) - quicksum(edges.values()) == 1)

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
            m.addConstr(n * edge_var_rev + labels[edge[1]] - labels[edge[0]] >= 1 - n*(1 - edge_var))
            m.addConstr(n * edge_var + labels[edge[0]] - labels[edge[1]] >= 1 - n*(1 - edge_var_rev))

    # allow only one arrow into each node
    for node in nodes:
        constraint_edges = [(u, v) for (u, v) in edges.keys() if v == node]
        m.addConstr(quicksum([edges[e] for e in constraint_edges]) <= 1)

    return m


def extract_solution(G, model):
    r""" Get the optimal prize collecting Steiner tree in G

        :param G: an ILPGraph
        :param model: a solved Gurobi model for Prize Collecting Steiner tree

        :return: the edges of an optimal prize collecting Steiner tree
    """
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return solution
