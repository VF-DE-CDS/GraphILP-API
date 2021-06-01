from gurobipy import Model, GRB, quicksum
import networkx as nx


def create_model(G, forced_terminals, weight='weight', prize='prize', warmstart=[]):
    r""" Create an ILP for the Prize Collecting Steiner Tree Problem.

    TODO Flow formulation.

    :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param terminals: a list of vertices that need to be connected by the Steiner tree
    :param weight: name of the argument in the edge dictionary of the graph used to store edge cost
    :param warmstart: a list of edges forming a tree in G connecting all terminals
    :param lower_bound: give a known lower bound to the solution length

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`_

    ILP:
        Let :math:`n = |V|` be the number of vertices in :math:`G` and :math:`T` the set of terminals.
        Further, let :math:`\overrightarrow{E} := \{(u, v), (v, u) \mid \{u, v\} \in E\}`
        be the directed edge set used in the internal representation.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{(u,v) \in \overrightarrow{E}} w_{uv} x_{uv}\\
            \text{s.t.} &&\\
            \forall \{u,v\} \in E: x_{uv} + x_{vu} \leq 1 && \text{(restrict edges to one direction)}\\
            \forall t \in T: x_t = 1 && \text{(require terminals to be chosen)}\\
            \sum_{v \in V} x_v - \sum_{(u, v) \in \overrightarrow{E}} x_{uv} = 1 && \text{(enforce cycle when graph}\\
            && \text{is not connected)}\\
            \forall \{u,v\}\in E: 2(x_{uv}+x_{vu}) - x_u - x_v \leq 0 && \text{(require vertices to be chosen}\\
            && \text{when edge is chosen)}\\
            \forall i \in V: x_i-\sum_{u=i \vee v=i}x_{uv} \leq 0 && \text{(forbid isolated vertices)}\\
            \forall \{u,v\}\in E: n x_{uv} + \ell_v - \ell_u \geq 1 - n(1-x_{vu}) && \text{(enforce increasing labels)}\\
            \forall \{u,v\}\in E: n x_{vu} + \ell_u - \ell_v \geq 1 - n(1-x_{uv}) && \text{(enforce increasing labels)}\\
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
    m = Model("PCST Flow")
    
    G.G = nx.DiGraph(G.G)

    terminals = [n for n in G.G.nodes() if G.G.nodes[n].get(prize, 0) > 0]
    n = G.G.number_of_nodes()
    T = len(terminals)
    root = forced_terminals[0]

    # add variables for edges and nodes
    edge_flow = m.addVars(G.G.edges(), vtype=GRB.INTEGER, lb=-T, ub=T)
    G.set_edge_vars(m.addVars(G.G.edges(), vtype=GRB.BINARY))
    G.set_node_vars(m.addVars(G.G.nodes(), vtype=GRB.BINARY))

    m.update()

    # abbreviations
    edges = G.edge_variables
    nodes = G.node_variables

    # set objective: minimise the sum of the weights of edges selected for the solution
    m.setObjective(quicksum([G.G.nodes[node].get(prize, 0) * node_var for node, node_var in nodes.items()])
                   - quicksum([edge_var * G.G.edges[edge][weight] for edge, edge_var in edges.items()]),
                   GRB.MAXIMIZE)
    
    # node can be chosen if an adjacent edge is chosen
    for node in G.G.nodes():
        m.addConstr(nodes[node] <= quicksum(edges[e] for e in G.G.edges(node)) + quicksum(edges[e] for e in G.G.in_edges(node)))


    # flow != 0 => edge chosen
    for edge, edge_var in edges.items():
        m.addConstr(2 * T * edge_var + edge_flow[edge] >= 0)
        m.addConstr(2 * T * edge_var - edge_flow[edge] >= 0)
    
    # flow condition on non-terminal nodes
    for node in G.G.nodes():
        if node not in terminals:
            m.addConstr(quicksum(edge_flow[e] for e in G.G.edges(node)) - quicksum(edge_flow[e] for e in G.G.in_edges(node)) == 0)
    
    # flow condition on root
    m.addConstr(quicksum(edge_flow[e] for e in G.G.edges(root)) - quicksum(edge_flow[e] for e in G.G.in_edges(root)) >= -T+1)
    
    # flow conditions on non-root terminal
    for t in terminals:
        if t != root:
            m.addConstr(quicksum(edge_flow[e] for e in G.G.edges(t)) - quicksum(edge_flow[e] for e in G.G.in_edges(t)) 
                        == nodes[t])

    m.update()



    return m


def extract_solution(G, model):
    r""" Get the optimal Steiner tree in G

        :param G: a weighted :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
        :param model: a solved Gurobi model for the minimum Steiner tree problem

        :return: the edges of an optimal Steiner tree connecting all terminals in G
    """
    solution = []

    for edge, edge_var in G.edge_variables.items():
        if edge_var.X > 0.5:
            solution.append(edge)

    return solution
