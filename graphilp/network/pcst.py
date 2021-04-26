from gurobipy import Model, GRB, quicksum
from networkx import Graph, find_cycle

# a dictionary translating edge variables to edge names for the callback
var2edge = None

# a dictionary translating edge names to edge variables for the callback
edge2var = None


def create_model(G, forced_terminals=[], weight='weight', prize='prize',
                warmstart=[], lower_bound=None):
    r""" Create an ILP for the Prize Collecting Steiner Tree Problem.

    This formulation enforces a cycle in the solution if it is not connected.
    A callback will detect cycles and add constraints to explicity forbid them.
    Together, this ensures that the solution is a tree.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param forced_terminals: list of terminals that have to be connected
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param prize: name of the argument in the vertex dictionary of the graph used to store vertex prize values
    :param warmstart: a list of edges forming a tree in G connecting all terminals
    :param lower_bound: give a known lower bound to the solution length

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    Callbacks:
        This model uses callbacks which need to be included when calling Gurobi's optimize function:

        model.optimize(callback = :obj:`callback_cycle`)

    ILP:
        Let :math:`T_f` be the set of forced terminals required to be part of the solution.
        Further, let :math:`p_v` be the prize associated with each vertex :math:`v`.

        .. math::
            :nowrap:

            \begin{align*}
            \max \sum_{v \in V} p_v x_v- \sum_{\{u,v\} \in E} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall \{u,v\}\in E: x_{uv} + x_{vu} \leq 1 && \text{(restrict edges to one direction)}\\
            \forall t \in T_f: x_t = 1 && \text{(require forced terminals to be chosen)}\\
            \sum_{v\in V} x_v - \sum_{\{u,v\}\in E} x_{uv} = 1 && \text{(enforce circle when graph is not connected)}\\
            \forall \{u,v\}\in E: 2x_{uv} - x_u - x_v \leq 0 && \text{(require vertices to be chosen when edge is chosen)}\\
            \forall i \in V: x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated vertices)}\\
            \end{align*}

        The callbacks add a new constraint for each cycle :math:`C` of length :math:`\ell(C)`
        coming up in a solution candidate:

        .. math::
            :nowrap:

            \begin{align*}
            \sum_{\{u, v\} \in C} x_{uv} < \ell(C) && \text{(forbid including complete cycle)}
            \end{align*}
    """
    global var2edge
    global edge2var

    # Create model
    m = Model("graphilp_pcst")
    m.Params.LazyConstraints = 1

    # Add variables for edges and nodes
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))

    m.update()

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables

    var2edge = dict(zip(edges.values(), edges.keys()))
    edge2var = edges

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([G.G.nodes[node].get(prize, 0) * node_var for node, node_var in nodes.items()])
                   - quicksum([edge_var * G.G.edges[edge].get(weight, 1) for edge, edge_var in edges.items()]),
                   GRB.MAXIMIZE)

    # equality constraints for terminals (each terminal needs to be chosen, i.e. set it's value to 1)
    for node, node_var in nodes.items():
        # the outer loop makes sure that terminals that are not in the graph are ignored
        if node in forced_terminals:
            m.addConstr(node_var == 1)

    # enforce cycle when graph is not connected
    m.addConstr(quicksum(nodes.values()) - quicksum(edges.values()) == 1)

    # if edge is chosen, both adjacent nodes need to be chosen
    for edge, edge_var in edges.items():
        m.addConstr(2*edge_var - nodes[edge[0]] - nodes[edge[1]] <= 0)

    # prohibit isolated vertices
    for node, node_var in nodes.items():
        edge_vars = [edge_var for edge, edge_var in edges.items() if (node == edge[0]) or (node == edge[1])]
        m.addConstr(node_var - quicksum(edge_vars) <= 0)
        
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

        # Include all edges and vertices from the warmstart in the solution:
        for edge in warmstart:
            if edge in edges:
                edges[edge].Start = 1
            else:
                edges[(edge[1], edge[0])].Start = 1

            nodes[edge[0]].Start = 1
            nodes[edge[1]].Start = 1

        m.update()    

    return m


def callback_cycle(model, where):
    """ Callback inserts constraints to forbid cycles in solution candidates
    
    :param model: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_
    :param where: a Gurobi callback parameter indicating from which step of the optimisation the callback
        originated    
    """
    if where == GRB.Callback.MIPSOL:
        # check for cycles whenever a new solution candidate is found
        variables = model.getVars()
        cur_sol = model.cbGetSolution(variables)

        # create graph from current solution
        solution = [var2edge[variables[i]] for i in range(len(variables)) if (cur_sol[i] > 0.5) and (variables[i]in var2edge)]
        G2 = Graph()
        G2.add_edges_from(solution)

        try:
            # find a cycle in the solution
            cycle = find_cycle(G2)
            cycle_idx = [edge if edge in var2edge.values() else (edge[1], edge[0]) for edge in cycle]

            # add new constraint
            model.cbLazy(quicksum([edge2var[edge] for edge in cycle_idx]) <= len(cycle_idx) - 1)

        except:
            # do nothing if no cycle was found
            return


def extract_solution(G, model):
    r""" Get the optimal prize collecting Steiner tree in G

        :param G: an ILPGraph
        :param model: a solved Gurobi model for Prize Collecting Steiner tree

        :return: the edges of an optimal prize collecting Steiner tree
    """
    solution = [edge for edge, edge_var in G.edge_variables.items() if edge_var.X > 0.5]

    return solution
