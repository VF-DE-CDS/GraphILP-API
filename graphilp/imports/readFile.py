import networkx as nx
import re

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
    root = 0

    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)

        # Found a new Edge
        if line.startswith('E '):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split(" ")
            edges.append((int(parts[1]), int(parts[2]), {'weight':int(parts[3])}))

            #print((tuple_data[0], tuple_data[1], {'weight':tuple_data[2]}))

        # Found a Terminal Node
        if line.startswith('TP '):
            parts = line.rstrip().split(" ")
            terminals.append((int(float(parts[1])), float(parts[2])))

        # Found root
        if line.startswith('RootP '):
            root = int(float(line.rstrip().split(" ")[1]))

    # Create a new NetworkX Graph object
    G = nx.Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)
    for n in G.nodes :
        G.nodes[n]['prize'] = 0
    for (t, p) in terminals:
        G.nodes[t]['prize'] = p

    return G, terminals

def stp_rooted_to_networkx(path):
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
    root = 0

    for line in lines:
        # Remove + characters. This is not always necessary
        line = re.sub(' +', ' ', line)

        # Found a new Edge
        if line.startswith('E\t'):
            # Extracting information(startingNode endingNode Distance)
            parts = line.rstrip().split("\t")[1:]

            # Parse the data into tuples and from Array of Integer and append to list of all edges
            tuple_data = tuple(int(float(p)) for p in parts)
            edges.append((tuple_data[0], tuple_data[1], {'weight':tuple_data[2]}))

        # Found a Terminal Node
        if line.startswith('TP '):
            parts = line.rstrip().split("\t\t")
            terminals.append((int(float(parts[0].rstrip().split(" ")[1])), float(parts[1])))

        # Found root
        if line.startswith('RootP '):
            root = int(float(line.rstrip().split(" ")[1]))

    # Create a new NetworkX Graph object
    G = nx.Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)
    for n in G.nodes :
        G.nodes[n]['prize'] = 0
    for (t, p) in terminals:
        G.nodes[t]['prize'] = p

    return G, terminals, root

