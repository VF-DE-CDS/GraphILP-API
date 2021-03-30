from graphilp.imports.ilpgraph import ILPGraph


def read(G):
    """ Wrap a NetworkX graph class by an ILPGraph class

    The wrapper class is used store the graph and the related variables of an optimisation problem
    in a single entity.

    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__

    :return: an :py:class:`~graphilp.imports.ilpgraph.ILPGraph`
    """

    result = ILPGraph()
    result.set_nx_graph(G)

    return result
