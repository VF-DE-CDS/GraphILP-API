import networkx as nx
from gurobipy import Model, GRB, quicksum


def get_var_names():
    node_var_name = 'node_{0}_is_included'
    arc_var_name = 'arc_({0},{1})_is_included'
    return node_var_name, arc_var_name

var2edge = None

def create_model(G_sa, art_root, forced_terminals=[], weight='weight', prize='prize',
                 warmstart=[], lower_bound=None):
    global var2edge
    global edge2var
    global node2var
    global root_sa
    global var2node
    global sap_instance

    m = Model("graphilp_pcst_morris")
    m.Params.LazyConstraints = 1

    root_sa = art_root
    sap_instance = G_sa.G




    # stick to gurobi workflow

    G_sa.set_edge_vars(m.addVars(G_sa.G.edges(), vtype=GRB.BINARY))
    G_sa.set_node_vars(m.addVars(G_sa.G.nodes(), vtype=GRB.BINARY))
    edges = G_sa.edge_variables
    nodes = G_sa.node_variables

    m.update()

    var2edge = dict(zip(edges.values(), edges.keys()))
    node2var = nodes
    edge2var = edges
    # stick to gurobi workflow



    # stick to gurobi workflow


    m.setObjective(quicksum([G_sa.G.nodes[node][prize] for node in G_sa.G.nodes]) +
                   quicksum([G_sa.G.edges[edge]['weight'] * edge_var for edge, edge_var in edges.items()]), GRB.MINIMIZE)

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
                              G_sa.G.nodes() if G_sa.G.nodes[terminal][prize] > 0]) == 1)


    # in-degree equations: every selected vertex has exactly one predecessor from path to root (25)
    for node in G_sa.G.nodes:
        if node == art_root:
            continue
        m.addConstr(quicksum(
            [edges[(pred, node)] for pred in G_sa.G.predecessors(node)]) == nodes[node])



        # flow balance constraints for non-customer vertices (30)
        if G_sa.G.nodes[node][prize] == 0 and not node in forced_terminals:
            # print('Adding:', quicksum([m.getVarByName('arc_({0},{1})_is_included'.format(neighbour, node)) for neighbour in self.G_sa.neighbors(node) if not neighbour==self.root_sa]) <= quicksum([m.getVarByName('arc_({0},{1})_is_included'.format(node, neighbour)) for neighbour in self.G_sa.neighbors(node) if not neighbour==self.root_sa]))
            m.addConstr(quicksum(
                [edges[(neighbour, node)] for neighbour in
                 G_sa.G.neighbors(node)]) <= quicksum(
                [edges[(node, neighbour)] for neighbour in
                 G_sa.G.neighbors(node)]))

        for neighbour in G_sa.G.neighbors(node):
            # every arc can only be oriented in one way (not necessary but speeds up optimization since it has not be added implicitly during separation) (31)
            m.addConstr(
                edges[(neighbour, node)] + edges[(node, neighbour)] <= nodes[node])


    m.update()

    return m


def callback_connect_constr(model, where):

    arc_attr_name = 'capacity'

    if where == GRB.Callback.MIPSOL:
        #print("INTERMEDIATE:", model.cbGet(GRB.Callback.MIPSOL_OBJ))
        # construct a graph from current solution (support graph)

        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)
        solution = [var2edge[variables[i]] for i in range(len(variables)) if
                    (cur_sol[i] > 0.5) and (variables[i] in var2edge)]

        G2 = nx.DiGraph()
        G2.add_weighted_edges_from([(sol[0], sol[1], 1.0) for sol in solution], weight=arc_attr_name)

        # Find all violated unconnected subsets
        for node in G2.nodes:
            if node == root_sa:
                continue

            cut_value, partition = nx.algorithms.flow.minimum_cut(G2, root_sa, node, capacity=arc_attr_name)
            if cut_value < 1:
                S_r, S_node = partition  # S_r contains root vertex r; S_node contains node node

                delta_Sr = out_cut_induced_by(S_r, sap_instance)  # pcst must be defined here
                for node_sr in S_r:

                    new_constraint = quicksum([edge2var[arc] for arc in delta_Sr]) >= node2var[node]
                    if not new_constraint in model.getConstrs():
                            model.cbLazy(new_constraint)


def extract_solution(G, model):
    r""" Get the optimal prize collecting Steiner tree in G
        :param G: an ILPGraph
        :param model: a solved Gurobi model for Prize Collecting Steiner tree
        :return: the edges of an optimal prize collecting Steiner tree
    """
    #solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]
    #for v in model.getVars():
    #    if v.x > 0:
    #        print('%s %g' % (v.varName, v.x))


    variables = model.getVars()
    #for edge, edge_var in G.edge_variables.items():
    #    print(edge_var.X)
    #    print(edge_var)
    #    print(edge)
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    #cur_sol = model.cbGetSolution(variables)
    #solution = [var2edge[variables[i]] for i in range(len(variables)) if
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



