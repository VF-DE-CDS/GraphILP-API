from gurobipy import Model, GRB, quicksum
import networkx as nx


def create_model(G, terminals, root=None, weight='weight', warmstart=[], lower_bound=None):
    r""" Create an ILP for the linear Steiner Problem.

    This formulation enforces a cycle in the solution if it is not connected.
    Cycles are then forbidden by enforcing an increasing labelling along the edges of the solution.
    To this end, the formulation is working with a directed graph internally.
    As a slight modification of :obj:`graphilp.network.steiner_linear`, the constraints enforce
    that the labels increase by one along each edge in the solution.

    :param G: an ILPGraph
    :param terminals: a list of nodes that need to be connected by the Steiner tree
    :param root: a termin chosen as the root of the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param warmstart: a list of edges forming a tree in G connecting all terminals
    :param lower_bound: give a known lower bound to the solution length

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`n = |V|` be the number of vertices in :math:`G`, :math:`T` the set of terminals,
        and :math:`r` be a terminal chosen as the root of the Steiner tree.
        Further, let :math:`\overrightarrow{E} := \{(u, v), (v, u) \mid \{u, v\} \in E\}`
        be the directed edge set used in the internal representation.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{(u,v) \in \overrightarrow{E}} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall \{u,v\} \in E: x_{uv} + x_{vu} \leq 1 && \text{(restrict edges to one direction)}\\
            x_r = 1 && \text{(require root to be chosen)}\\
            \forall t \in T: x_t = 1 && \text{(require terminals to be chosen)}\\
            \sum_{v \in V} x_v - \sum_{(u, v) \in \overrightarrow{E}} x_{ij} = 1 && \text{(enforce circle when graph}\\
            && \text{is not connected)}\\
            \forall \{u,v\}\in E: 2(x_{uv}+x_{vu}) - x_u - x_v \leq 0 && \text{(require vertices to be chosen}\\
            && \text{when edge is chosen)}\\
            \forall i \in V: x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated nodes)}\\
            \forall \{u,v\}\in E: \ell_v - 2nx_{vu} \leq \ell_u + 1 + 2n(1-x_{uv}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: \ell_u + 1 \leq 2nx_{vu} + \ell_v + 2n(1-x_{uv}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: \ell_u - 2nx_{uv} \leq \ell_v + 1 + 2n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: \ell_v + 1 \leq 2nx_{uv} + \ell_u + 2n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall v \in V: \ell_v - n x_v \leq 1&& \text{(set label to 1 when}\\
            && \text{vertex is not chosen)}\\
            \forall v \in V: \sum_{(u,v) \in \overrightarrow{E}} x_{uv} \leq 1 && \text{(only one arrow into each vertex)}\\
            \end{align*}

    Example:
            .. list-table::
               :widths: 50 50
               :header-rows: 0

               * - .. image:: images/example_steiner.png
                 - `Steiner trees <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/SteinerTreesOnStreetmap.ipynb>`_

                   Find the shortest tree connecting a given set of nodes in a graph.
    """
    # create model
    m = Model("Steiner Tree")

    n = G.G.number_of_nodes()

    # If no root is specified, set it to be the first terminal in the terminals list
    if (root is None):
        root = terminals[0]

    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))
    edge_set = set(G.G.edges())
    edge_set = edge_set.union({(v, u) for u, v in edge_set})
    G.set_edge_vars(m.addVars(edge_set, vtype=GRB.BINARY))

    # node label variables used to avoid cycles
    G.set_label_vars(m.addVars(G.G.nodes(), vtype=GRB.INTEGER, lb=1))

    m.update()

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables
    labels = G.label_variables
    edge2var = dict(zip(edges.keys(), edges.values()))

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]), GRB.MINIMIZE)

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

    # enforce cycle when graph is not connected
    m.addConstr(quicksum(nodes.values()) - quicksum(edges.values()) == 1)

    # at most one direction per edge can be chosen
    m.addConstrs(edges[(u, v)] + edges[(v, u)] <= 1 for u, v in G.G.edges())

    # if edge is chosen, both adjacent nodes need to be chosen
    m.addConstrs(2*(edges[(u, v)] + edges[(v, u)]) - nodes[u] - nodes[v] <= 0 for u, v in G.G.edges())

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
    for u, v in G.G.edges():
        m.addConstr(labels[v] - 2 * n * edges[(v, u)] <= labels[u] + 1 + 2*n*(1 - edges[(u, v)]))
        m.addConstr(labels[u] + 1 <= 2*n*edges[(v, u)] + labels[v] + 2*n*(1 - edges[(u, v)]))
        m.addConstr(labels[u] - 2*n*edges[(u, v)] <= labels[v] + 1 + 2*n*(1 - edges[(v, u)]))
        m.addConstr(labels[v] + 1 <= 2*n*edges[(u, v)] + labels[u] + 2*n*(1 - edges[(v, u)]))
    
    # set label to 1 if node is not chosen
    for v in G.G.nodes():
        m.addConstr(labels[v] - n * nodes[v] <= 1)            

    # allow only one arrow into each node
    for node in nodes:
        constraint_edges = [(u, v) for (u, v) in edges.keys() if v == node]
        m.addConstr(quicksum([edges[e] for e in constraint_edges]) <= 1)

    # set lower bound
    if lower_bound:
        m.addConstr(quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]) >= lower_bound)

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
