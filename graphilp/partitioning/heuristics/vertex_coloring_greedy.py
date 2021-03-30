def _first_available(color_list):
    """
    (https://en.wikipedia.org/wiki/Greedy_coloring)
    Return smallest non-negative integer not in the given list of colors.

    :param color_list: List of neighboring nodes colors
    :type color_list: list of int
    :rtype: int
    """
    color_set = set(color_list)
    count = 0

    while True:
        if count not in color_set:
            return count
        count += 1


def get_heuristic(G):
    """ Greedy colouring heuristic

    (explanation and code: https://en.wikipedia.org/wiki/Greedy_coloring)

    :param G: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    :return: two dictionaries: {color_1:[list_of_color_1_nodes], ...} and {node_1:color_of_node_1, ...}
    """
    nodes = G.G.nodes()

    node_to_col = {}
    col_to_node = {}

    for node in nodes:
        neighbor_colors = [node_to_col.get(neigh_node) for neigh_node in G.G.neighbors(node)]
        node_color = _first_available(neighbor_colors)
        node_to_col[node] = node_color
        if node_color not in col_to_node:
            col_to_node[node_color] = [node]
        else:
            col_to_node.get(node_color).append(node)

    return col_to_node, node_to_col
