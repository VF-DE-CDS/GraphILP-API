from gurobipy import Model, GRB, quicksum
import networkx as nx


def get_var_names():
    node_var_name = 'node_{0}_is_included'
    arc_var_name = 'arc_({0},{1})_is_included'
    return node_var_name, arc_var_name

var2edge = None

def create_model(G, G_sa, art_root, forced_terminals=[], weight='weight', prize='prize',
                 warmstart=[], lower_bound=None):
    global var2edge
    global edge2var
    global node2var
    global root_sa
    global var2node
    global sap_instance

    sap_instance = G_sa



    m = Model("graphilp_pcst_morris")
    m.Params.LazyConstraints = 1

    root_sa = art_root
    """
    initiates gurobi model and adds constraints except for connectivity constraints
    self.G_sa must exist
    """
    edges = dict()
    nodes = dict()



    # add binary variables: every vertex and every edge has one variable
    for node in G_sa.nodes:
        nodes[node] = (m.addVar(vtype=GRB.BINARY, name='node_{0}_is_included'.format(node)))
    for arc in G_sa.edges:
        # print('arc_({0},{1})_is_included'.format(arc[0], arc[1]))
        edges[arc] = (m.addVar(vtype=GRB.BINARY, name='arc_({0},{1})_is_included'.format(arc[0], arc[1])))
    m.update()
    var2edge = dict(zip(edges.values(), edges.keys()))
    node2var = nodes
    edge2var = edges
    # stick to gurobi workflow


    m.setObjective(quicksum([G.nodes[node][prize] for node in G.nodes]) +
                   quicksum([G_sa.edges[edge]['weight'] * edge_var for edge, edge_var in edges.items()]), GRB.MINIMIZE)

    # add init constraints
    """
    adds:
        1. root constraints-- roots must be contained in feasible solution
    """
    m.addConstr(nodes[art_root] == 1)


    if forced_terminals != []:
        for node, node_var in nodes.items():
            # the outer loop makes sure that terminals that are not in the graph are ignored
            if node in forced_terminals:
                m.addConstr(node_var == 1)
                m.addConstr(edges[(art_root, node)] == 1)

    # artificial root must have exactly one connection (27)
    else:
         m.addConstr(quicksum(
            [edges[(art_root, terminal)] for terminal in
                              G.nodes() if G.nodes[terminal][prize] > 0]) == 1)


    # in-degree equations: every selected vertex has exactly one predecessor from path to root (25)
    for node in G_sa.nodes:
        if node == art_root:
            continue
        m.addConstr(quicksum(
            [edges[(pred, node)] for pred in G_sa.predecessors(node)]) == nodes[node])



        # flow balance constraints for non-customer vertices (30)
        if G.nodes[node][prize] == 0 and not node in forced_terminals:
            # print('Adding:', quicksum([m.getVarByName('arc_({0},{1})_is_included'.format(neighbour, node)) for neighbour in self.G_sa.neighbors(node) if not neighbour==self.root_sa]) <= quicksum([m.getVarByName('arc_({0},{1})_is_included'.format(node, neighbour)) for neighbour in self.G_sa.neighbors(node) if not neighbour==self.root_sa]))
            m.addConstr(quicksum(
                [edges[(neighbour, node)] for neighbour in
                 G_sa.neighbors(node)]) <= quicksum(
                [edges[(node, neighbour)] for neighbour in
                 G_sa.neighbors(node)]))

        for neighbour in G_sa.neighbors(node):
            # every arc can only be oriented in one way (not necessary but speeds up optimization since it has not be added implicitly during separation) (31)
            m.addConstr(
                edges[(neighbour, node)] + edges[(node, neighbour)] <= nodes[node])


    m.update()

    return m


def callback_connect_constr(model, where):
    arc_attr_name = 'capacity'
    # if where == GRB.Callback.MIPSOL:
    #
    #    #construct a graph from current solution (support graph)
    #    G_sup = connectivity.__sup_graph_from_model__(model, arc_attr_name=arc_attr_name, where='MIPSOL')
    #    connectivity.add_violated_constraints(model, G_sup, arc_attr_name)
    # print('In MIPSOL')

    if where == GRB.Callback.MIPSOL:
        # print('In MIPSOL')
        # construct a graph from current solution (support graph)
        # where = Model
        # create graph from current solution
        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)
        solution = [var2edge[variables[i]] for i in range(len(variables)) if
                    (cur_sol[i] > 0.5) and (variables[i] in var2edge)]

        G2 = nx.DiGraph()
        G2.add_weighted_edges_from([(sol[0], sol[1], 1.0) for sol in solution],
                                      weight=arc_attr_name)





        # for all pairs of nodes in G_sup check whether they are connected to the root
        # for comb in combinations(G_sup.nodes, 2):
        # TODO: find a way such that pcst must not be defined here (terrible hack because gurobi does not allow method as callback funtion)

        artificial_root = root_sa
        violated_count = 0
        max_count = float('inf')


        for node in G2.nodes:
            if node == artificial_root:
                continue
            cut_value, partition = nx.algorithms.flow.minimum_cut(G2, artificial_root, node, capacity=arc_attr_name)
            if round(cut_value, 3) < round(1, 3):

                # print('{0} and {1} are not connected.'.format(artificial_root, node))
                S_r, S_node = partition  # S_r contains root vertex r; S_node contains node node
                # print(S_r, S_node)
                # TODO: find a way such that pcst must not be defined here (terrible hack because gurobi does not allow method as callback funtion)
                delta_Sr = out_cut_induced_by(S_r, sap_instance)  # pcst must be defined here
                for node_sr in S_r:
                    # print('Adding: ', gurobipy.quicksum([model.getVarByName(arc_var_name.format(arc[0], arc[1])) for arc in delta_Sr])>=model.getVarByName(node_var_name.format(node)))
                    new_constraint = quicksum(
                        [edge2var[arc] for arc in
                         delta_Sr]) >= node2var[node_sr]
                    if not new_constraint in model.getConstrs():

                            model.cbLazy(new_constraint)

        return violated_count > 0


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

def in_cut_induced_by(S, G):
    """
    """
    delta_S = []
    for node in S:
        # get all adjacent edges
        all_pred = G.predecessors(node)
        # check whether exactly one endpoint is in S
        for node2 in all_pred:
            if node2 in S and not node in S:
                delta_S.append((node, node2))
    return delta_S

