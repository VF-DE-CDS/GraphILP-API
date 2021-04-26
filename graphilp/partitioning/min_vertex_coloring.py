from gurobipy import Model, GRB, quicksum


def create_model(G, bound_num_colors=-1, warmstart={}):
    r"""
    Create an ILP for minimum vertex colouring.

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param bound_num_colors: an upper bound on the number of colours needed in a minimum vertex colouring
    :param warmstart: a dictionary mapping vertices to colours such that connected vertices have different colours

    :return: a `gurobipy model <https://www.gurobi.com/documentation/9.1/refman/py_model.html>`__

    ILP:
        We allow for up to :math:`H` colours to be used in the solution (if no better bound is given
        by bound_num_colors, assume :math:`H=|V|`) and introduce variables :math:`w_i` indicating whether
        colour :math:`i` is used in the solution. Variables :math:`x_{vi}` indicate whether colour :math:`i`
        is assigned to vertex :math:`v`.

        .. math::
            :nowrap:

            \begin{align*}
            \min \sum_{1\le i \le H}w_{i} && \text{ (minimize the total number of colours used) }\\
            \text{s.t.} \\
            \forall v\in V: \sum_{i=1}^{H} x_{vi} = 1\ && \text{ (every vertex gets exactly one colour) } \\
            \forall(u,v)\in E, i \in \{1,\ldots,H\}:\\
            x_{ui}+x_{vi}\le w_{i}\ && \text{ (neighbours do not get the same colour) } \\
            \forall v\in V, i \in \{1,\ldots, H\}:\\
            x_{vi},w_{i}\in\{0,1\}\ && \text{ (assigning a colour is a binary decision) }\\
            \forall i\in\{1, \ldots, H-1\}: w_{i} \leq w_{i-1} &&
            \text{(only assign colour } i \text{ if colour } i-1 \text{ is assigned)}
            \end{align*}

    Examples:
        .. list-table::
           :widths: 50 50
           :header-rows: 0

           * - .. image:: images/example_mapcolouring.png
             - `Map colouring <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/MapColouring.ipynb>`_

               Colour a map with as few colours as possible such that

               no two adjacent areas get the same colour.
           * - .. image:: images/example_vertexcolour.png
             - `Minimum vertex cover <https://github.com/VF-DE-CDS/GraphILP-API/blob/develop/graphilp/examples/MinVertexColouring.ipynb>`_

               A simple example finding the minimal number of colours needed

               to colour circle graphs such that neighbouring nodes get different colours.
    """
    # initialize model
    m = Model('graphilp_min_vertex_coloring')

    nodes = G.G.nodes()
    edges = G.G.edges()

    # add decision variables
    if bound_num_colors > -1:
        max_number_colors = bound_num_colors
    else:
        if len(warmstart) > 0:
            max_number_colors = len(set(warmstart.values()))
        else:
            max_number_colors = G.G.number_of_nodes()

    color_used_vars = m.addVars(max_number_colors, name='color_used', vtype=GRB.BINARY)

    # whether or not each vertex is assigned to color c
    node_color_vars = m.addVars(nodes, max_number_colors, name='color_assignment', vtype=GRB.BINARY)
    G.node_assignment_variables = node_color_vars

    m.update()

    # objective is to minimize the number of colors used
    m.setObjective(quicksum(color_used_vars), GRB.MINIMIZE)

    # for each node: exactly one color must be assigned
    for node in nodes:
        m.addConstr(node_color_vars.sum(node, '*') == 1)

    # two neighboring nodes cannot have the same color assigned
    for edge in edges:
        m.addConstrs(node_color_vars[edge[0], color] + node_color_vars[edge[1], color] <= color_used_vars[color] for color in color_used_vars)

    # strengthen formulation
    for i in range(1, len(color_used_vars)):
        m.addConstr(color_used_vars[i] <= color_used_vars[i-1])  # only assign color i if color i-1 is assigned already

    m.update()

    # set warmstart
    if len(warmstart) > 0:
        for var in color_used_vars.values():
            var.Start = 1

        for var in node_color_vars.values():
            var.Start = 0

        for node, node_color in warmstart.items():
            node_color_vars[node, node_color].Start = 1

        m.update()

    return m


def extract_solution(G, model):
    """
    Get a dictionary mapping colours to lists of vertices

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :param model: a solved Gurobi model for the minimum Steiner tree problem

    :return: a dictionary mapping colours to lists of vertices
    """

    col_to_node = {}
    node_to_col = {}

    for var, sol_var in G.node_assignment_variables.items():
        if sol_var.X > 0.5:
            color = var[1]
            node = var[0]

            node_to_col[node] = color

            if color not in col_to_node.keys():
                col_to_node[color] = [node]
            else:
                col_to_node.get(color).append(node)

    return col_to_node, node_to_col
