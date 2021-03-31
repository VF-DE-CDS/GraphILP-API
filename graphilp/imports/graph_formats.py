from networkx import Graph
import re


def edges_to_networkx(path):
    """
    Creates a NetworkX Graph from an .edges file (`Network Repository format <http://networkrepository.com>`__).

    Network Repository is a large collection of network graph data for research and benchmarking.

    :param path: path to .edges file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    with open(path, "rt") as input_file:
        lines = input_file.readlines()
    edges = []

    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)
        # Found a new Edge
        # Extracting information(startingNode endingNode Distance)
        parts = line.rstrip().split(" ")

        # Parse the data into tuples and from Array of Integer and append to list of all edges
        tuple_data = tuple(int(p) for p in parts[:2])
        edges.append((tuple_data[0], tuple_data[1]))

    # Create a new NetworkX Graph object
    G = Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G


def stp_to_networkx(path):
    """
    Creates a NetworkX Graph from an .stp file (`SteinLib format <http://steinlib.zib.de/format.php>`__).

    `SteinLib <http://steinlib.zib.de/steinlib.php>`__ is a collection of Steiner tree
    problems in graphs and variants.

    The format description can be found `here <http://steinlib.zib.de/format.php>`__ on the SteinLib pages.

    :param path: path to .stp file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
        and a list of terminals

    Example:
        G, terminals = stp_to_networkx("steinlib_instance.stp")
    """
    with open(path, "rt") as input_file:
        lines = input_file.readlines()

    edges = []
    terminals = []

    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)

        # Found a new Edge
        if line.startswith('E '):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split(" ")[1:]

            # Parse the data into tuples and from Array of Integer and append to list of all edges
            tuple_data = tuple(int(p) for p in parts)
            edges.append((tuple_data[0], tuple_data[1], {'weight': tuple_data[2]}))

        # Found a Terminal Node
        if line.startswith('T '):
            terminals.append(int(line.rstrip().split(" ")[1]))

    # Create a new NetworkX Graph object
    G = Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G, terminals


def mis_to_networkx(path):
    """
    Creates a NetworkX Graph from a .mis file (ASCII DIMACS graph format).

    This is used for maximum independet set benchmarking data
    from `BHOSLIB <http://sites.nlsde.buaa.edu.cn/~kexu/benchmarks/graph-benchmarks.htm>`__.

    :param path: path to .edges file
    :type path: str
    :returns: a `NetworkX Graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    """
    with open(path, "rt") as input_file:
        lines = input_file.readlines()

    edges = []

    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)

        # Found a new Edge
        if line.startswith('e '):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split(" ")[1:]

            # Parse the data into tuples and from Array of Integer and append to list of all edges
            tuple_data = tuple(int(p) for p in parts)
            edges.append((tuple_data[0], tuple_data[1]))

    # Create a new NetworkX Graph object
    G = Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G
