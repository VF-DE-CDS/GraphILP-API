import networkx as nx
from gurobipy import Model, GRB, quicksum


var2edge = None


def create_model(G_sa, art_root, forced_terminals=None, weight='weight', prize='prize'):
    """

    :param G_sa: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph` (Originial graph has to be transformed to a Steiner Arborescence Problem)
    :param art_root: Artificial root of the Steiner Arborescence Problem
    :param forced_terminals: list of terminals that have to be connected
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param prize: name of the argument in the node dictionary of the graph used to store node prize values


    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    Create an ILP for the Prize Collecting Steiner Tree Problem.

    This formulation enforces a cycle in the solution if it is not connected.
    Cycles are then forbidden by enforcing an increasing labelling along the edges of the solution.
    To this end, the formulation is working with a directed graph internally.

    Callbacks:
        This model uses callbacks which need to be included when calling Gurobi's optimize function:
        model.optimize(callback = :obj:`callback_connect_constr`)

    ILP:
        Let :math:`V_{SA}` be the set of vertices in the graph and  :math:`A_{SA}` be the directed edge set used in the internal representation.
        Let :math:`T_f` be the set of forced terminals required to be part of the solution.
        Further, let :math:`p^{\prime}_{v}` be the prize associated with each vertex :math:`v` and
        :math:`c^{\prime\prime}_{uv}`
        be the cost associated with each edge :math:`(u, v)`.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{ij \in A_{SA}} c^{\prime\prime}_{uv}x_{uv} + \sum_{u \in V_{SA}} p^{\prime}_{u}\\
            \text{s.t.} &&\\
            x_u - \sum_{vu \in A_{SA}} x_{vu} = 0 && \forall u \in V_{SA} \setminus r  && \text{(forbid isolated vertices)}\\
            \sum_{ru \in A_{SA}} x_{ru} = 1 && \text{(root has to be connected to exactly one node)}\\
            \forall t \in T_f: x_t = 1 && \text{(require forced terminals to be chosen)}\\
            x_{uv}, x_u \in \{0, 1\} && \forall (u, v) \in A_{SA}, \forall u \in V_{SA} \setminus r
            \end{align*}
        The callbacks add a new constraint for each cut :math:`C` of length :math:`\ell(C)`
        coming up in a solution candidate:
        .. math::
            :nowrap:
            \begin{align*}
            x(\delta^{-}(S)) \geq x_k && k \in S, r \not\in S, \forall S \subset V_{SA} && \text{(cut constraints)}\\
            \end{align*}
    """

    if forced_terminals is None:
        forced_terminals = []
    global var2edge
    global edge2var
    global node2var
    global root_sa
    global var2node
    global sap_instance

    # Create model
    m = Model("graphilp_pcst_morris")
    m.Params.LazyConstraints = 1

    root_sa = art_root
    sap_instance = G_sa.G

    # Add variables for edges and nodes
    G_sa.set_edge_vars(m.addVars(G_sa.G.edges(), vtype=GRB.BINARY))
    G_sa.set_node_vars(m.addVars(G_sa.G.nodes(), vtype=GRB.BINARY))
    edges = G_sa.edge_variables
    nodes = G_sa.node_variables

    m.update()

    # abbreviations
    var2edge = dict(zip(edges.values(), edges.keys()))
    node2var = nodes
    edge2var = edges

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([G_sa.G.nodes[node][prize] for node in G_sa.G.nodes]) +
                   quicksum([G_sa.G.edges[edge][weight] * edge_var for edge, edge_var in edges.items()]),
                   GRB.MINIMIZE)

    # add init constraints

    #enforce artificial root
    m.addConstr(nodes[art_root] == 1)

    if forced_terminals:
        for node, node_var in nodes.items():
            # the outer loop makes sure that terminals that are not in the graph are ignored
            if node in forced_terminals:
                m.addConstr(node_var == 1)
                m.addConstr(edges[(art_root, node)] == 1)

    # artificial root must have exactly one connection (27)
    else:
        m.addConstr(quicksum(
            [edges[(art_root, terminal)] for terminal in
             G_sa.G.nodes() if G_sa.G.nodes[terminal][prize] > 0]) == 1)

    # in-degree equations: every selected vertex has exactly one predecessor from path to root (25)
    for node in G_sa.G.nodes:
        if node == art_root:
            continue
        m.addConstr(quicksum(
            [edges[(pred, node)] for pred in G_sa.G.predecessors(node)]) == nodes[node])

        # flow balance constraints for non-customer vertices (30)
        if G_sa.G.nodes[node][prize] == 0 and not node in forced_terminals:
            # print('Adding:', quicksum([m.getVarByName('arc_({0},{1})_is_included'.format(neighbour, node)) for
            # neighbour in self.G_sa.neighbors(node) if not neighbour==self.root_sa]) <= quicksum([m.getVarByName(
            # 'arc_({0},{1})_is_included'.format(node, neighbour)) for neighbour in self.G_sa.neighbors(node) if not
            # neighbour==self.root_sa]))
            m.addConstr(quicksum(
                [edges[(neighbour, node)] for neighbour in
                 G_sa.G.neighbors(node)]) <= quicksum(
                [edges[(node, neighbour)] for neighbour in
                 G_sa.G.neighbors(node)]))

        for neighbour in G_sa.G.neighbors(node):
            # every arc can only be oriented in one way (not necessary but speeds up optimization since it has not be added implicitly during separation) (31)
            m.addConstr(
                edges[(neighbour, node)] + edges[(node, neighbour)] <= nodes[node])
    #delta_Sr = [(1, 12), (1, 13), (1, 15), (1, 16), (1, 17), (1, 18), (1, 19), (1, 21), (1, 23), (1, 24), (1, 25), (1, 26), (1, 27), (1, 28), (1, 30), (1, 31), (1, 33), (1, 34), (1, 35), (1, 37), (1, 40), (1, 41), (1, 42), (1, 43), (1, 47), (1, 56), (1, 60), (1, 63), (1, 64), (1, 66), (1, 67), (1, 68), (1, 72), (1, 77), (1, 79), (1, 80), (1, 82), (1, 83), (1, 84), (1, 85), (1, 88), (1, 90), (1, 91), (1, 98), (1, 101), (1, 104), (1, 106), (1, 107), (1, 110), (1, 112), (1, 126), (1, 127), (1, 131), (1, 134), (1, 136), (1, 143), (1, 147), (1, 162), (1, 178), (1, 182), (1, 183), (1, 187), (1, 188), (1, 197), (1, 198), (1, 207), (1, 209), (1, 201), (1, 215), (1, 216), (1, 210), (1, 223), (1, 221), (1, 234), (1, 245), (1, 247), (1, 248), (1, 258), (1, 259), (1, 261), (1, 268), (1, 282), (1, 287), (1, 291), (1, 292), (1, 297), (1, 301), (1, 303), (1, 311), (1, 314), (1, 321), (1, 329), (1, 330), (1, 341), (1, 343), (1, 345), (1, 353), (1, 357), (1, 370), (1, 379)
    # , (1, 473), (1, 628), (1, 640), (1, 641), (1, 650), (1, 652), (1, 686), (1, 713), (1, 723), (1, 741)]
    #m.addConstr(quicksum([edges[arc] for arc in delta_Sr]) >= nodes[738])

    m.update()

    return m


def callback_connect_constr(model, where):
    arc_attr_name = 'capacity'
    if where != 0 and where != 6:
        print(where)
    """

    if where == GRB.Callback.MIPSOL:
        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)
        solution = [var2edge[variables[i]] for i in range(len(variables)) if (cur_sol[i] > 0.5) and (variables[i] in var2edge)]
        G2 = nx.DiGraph()
        G2.add_weighted_edges_from([(sol[0], sol[1], 1) for sol in solution], weight=arc_attr_name)
        # Find all violated unconnected subsets
        for node in G2.nodes:
            if node == root_sa:
                continue

            cut_value, partition = nx.algorithms.flow.minimum_cut(G2, root_sa, node, capacity=arc_attr_name)
            if cut_value < 1 - 0.0001:
                S_r, S_node = partition  # S_r contains root vertex r; S_node contains node node

                delta_Sr = out_cut_induced_by(S_r, sap_instance)  # pcst must be defined here
                # for node_sr in S_r:

                new_constraint = quicksum([edge2var[arc] for arc in delta_Sr]) >= node2var[node]
                model.cbLazy(new_constraint)

    """

    if where == GRB.Callback.MIPNODE:
        variables = model.getVars()
        cur_sol = model.cbGetNodeRel(variables)
        solution = [(var2edge[variables[i]], cur_sol[i]) for i in range(len(variables)) if (cur_sol[i] > 0) and (variables[i] in var2edge)]
        G2 = nx.DiGraph()
        G2.add_weighted_edges_from([(sol[0][0], sol[0][1], sol[1]) for sol in solution], weight=arc_attr_name)
        # Find all violated unconnected subsets
        for node in G2.nodes:
            if node == root_sa:
                continue

            cut_value, partition = nx.algorithms.flow.minimum_cut(G2, root_sa, node, capacity=arc_attr_name)
            if cut_value < 1 - 0.0001:
                S_r, S_node = partition  # S_r contains root vertex r; S_node contains node node

                delta_Sr = out_cut_induced_by(S_r, sap_instance)  # pcst must be defined here
                #for node_sr in S_r:
                new_constraint = quicksum([edge2var[arc] for arc in delta_Sr]) >= node2var[node]
                model.cbLazy(new_constraint)


def extract_solution(G, model):
    r""" Get the optimal prize collecting Steiner tree in G
        :param G: an ILPGraph
        :param model: a solved Gurobi model for Prize Collecting Steiner tree
        :return: the edges of an optimal prize collecting Steiner tree
    """
    # solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]
    # for v in model.getVars():
    #    if v.x > 0:
    #        print('%s %g' % (v.varName, v.x))

    variables = model.getVars()
    # for edge, edge_var in G.edge_variables.items():
    #    print(edge_var.X)
    #    print(edge_var)
    #    print(edge)
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    # cur_sol = model.cbGetSolution(variables)
    # solution = [var2edge[variables[i]] for i in range(len(variables)) if
    #            (cur_sol[i] > 0.5) and (variables[i] in var2edge)]
    return solution


def out_cut_induced_by(S, G):
    """
    """
    delta_S = []
    for node in S:
        # get all adjacent edges
        all_succ = G.successors(node)
        # check whether exactly one endpoint is in S
        for node2 in all_succ:
            if node in S and not node2 in S:
                delta_S.append((node, node2))
    return delta_S
