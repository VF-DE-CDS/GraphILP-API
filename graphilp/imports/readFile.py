from graphilp.imports import ilpgraph
import networkx as nx
import re
from scipy.sparse import csc_matrix
import numpy as np

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
    G = nx.Graph()

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
    G = nx.Graph()

    # Fill the graph with our edges. This method automatically fills in the nodes as well.
    G.add_edges_from(edges)

    return G

def col_file_to_networkx(path):
    """
    Creates a networkx object given a path to a .col file.
    A .col file only contains edges. Each line starting with an "e" is followed by both edge's points.

    :param path: path to .col file
    :type path: str
    :rtype: networkx undirected graph
    """

    edges_list = []

    with open(path) as f:
        for line in f.readlines():
            if line.startswith('e'):
                line = line.replace('/n', '')
                line_splitted = line.split()
                edge = (line_splitted[1], line_splitted[2])
                edges_list.append(edge)

    G = nx.Graph()
    G.add_edges_from(edges_list)
    return G

def read_set_cover(path):
    """ Reads an instance of a setCover Problem instance taken from the OR - Library
    http://people.brunel.ac.uk/~mastjjb/jeb/orlib/scpinfo.html
    Columns are Sets, Rows are Nodes contained in the Sets

    Formatting of such a file with a cost vector c is as follows
    Row 1 : number of rows (m), number of columns (n)
    Row 2 onwards: the cost of each column c(j),j=1,...,n

    Next section:
    Row 1: the amount of columns which cover cover the row i
    Row 2 onwards: list of the columns which cover row i


    :param path: path to .txt file

    :returns: sparse matrix and sets
    """
    sets = dict()
    curSet = 0
    curRow = 0
    readElements = 0
    curRowLength = 0

    with open(path, "rt") as input_file:
        lines = input_file.readlines()

    # Split first line by spaces
    line = lines[0].split(" ")

    # Information about total number of nodes and sets are contained in the first line
    numNodes = int(line[1])
    numSets = int(line[2])

    # Creating empty array
    sparseMatrix = csc_matrix((numNodes, numSets), dtype = np.int8).toarray()

    # Pop so we don't have to skip it in the first step of the loop
    lines.pop(0)

    for line in lines:
        # Split After Spaces
        curLine = line.split(" ")
        # As long as we are in the first section, read out the costs of the sets
        if curSet < numSets:
            # Each element/column is a set
            for element in curLine:
                # Only extract numeric values and no special characters
                if element != '' and element != '\n':
                    # Create a new entry in the dictionary including the weight of the set
                    sets[curSet] = dict(weight = int(element))
                    curSet += 1
            continue

        # Arrived at the other section, i.e. the section where detailed information about every set is given
        else:
            # Amount of Sets that contain node i is always stored in the first row of node i's section
            if (curRow == 0 and curRowLength == 0):
                curRowLength = int(curLine[1])
            # curRowLength doesn't denote the actual length of the  row in the text file.
            # It rather specifies the amount of elements which have to be read in total
            # Since the information iteself is split over many lines, we have to keep track of the total amount of
            # elements read.
            if readElements >= curRowLength:
                curRow += 1
                curRowLength = int(curLine[1])
                readElements = 0
            else:
                # Add every element to the sparse matrix containing
                for element in curLine:
                    if element != '' and element != '\n':
                        sparseMatrix[curRow][int(element) - 1] = 1
                        readElements += 1

    return sparseMatrix, sets